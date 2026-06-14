"""Load reference tickets for hyperlink detail views (SQLite or lazy corpus seed)."""
from __future__ import annotations

import json
import re
from typing import Optional

from sqlalchemy.orm import Session

from src.data.rag_corpus_catalog import (
    RagCatalogEntry,
    citation_label_to_ticket_id,
    is_corpus_ticket_id,
    iter_rag_catalog_entries,
)
from src.config.departments import canonical_department, department_for_category
from src.data.rag_demo_corpus import demo_ticket_routing
from src.data.synthetic_corpus import load_synthetic_raw
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket, User

_INC_REF_RE = re.compile(r"^INC-([A-F0-9]{8})$", re.I)
_SYN_REF_RE = re.compile(r"^SYN-(\d{4})$", re.I)


def is_synthetic_ticket_id(ticket_id: str | None) -> bool:
    """True for 1k synthetic RAG corpus rows (syn-0001 … syn-1000)."""
    tid = (ticket_id or "").strip().lower()
    return tid.startswith("syn-")


def is_reference_seed_id(ticket_id: str | None) -> bool:
    """Historical / seed ticket opened from a resolution reference link."""
    return is_corpus_ticket_id(ticket_id) or is_synthetic_ticket_id(ticket_id)


def normalize_reference_ticket_id(ticket_id: str) -> str:
    tid = (ticket_id or "").strip()
    if is_corpus_ticket_id(tid):
        return tid.lower()
    if is_synthetic_ticket_id(tid):
        return tid.lower()
    return tid


def resolve_reference_label(label_or_id: str) -> Optional[str]:
    """
    Map a citation label to a corpus ticket_id without hitting the DB.
    KB-DB-DEDUP -> rag-h3-09; RAG-H3-09 -> rag-h3-09.
    """
    raw = (label_or_id or "").strip()
    if not raw:
        return None

    mapped = citation_label_to_ticket_id().get(raw.upper())
    if mapped:
        return mapped

    if is_corpus_ticket_id(raw):
        return normalize_reference_ticket_id(raw)

    syn = _SYN_REF_RE.match(raw)
    if syn:
        return f"syn-{syn.group(1)}"

    if is_synthetic_ticket_id(raw):
        return raw.strip().lower()

    return None


def resolve_reference_link(session: Session, label_or_id: str) -> Optional[str]:
    """Resolve any reference label/id to a ticket_id (corpus or user)."""
    raw = (label_or_id or "").strip()
    if not raw:
        return None

    canon = resolve_reference_label(raw)
    if canon:
        return canon

    for key in (raw, raw.lower()):
        hit = session.get(Ticket, key)
        if hit:
            return hit.ticket_id

    inc = _INC_REF_RE.match(raw)
    if inc:
        prefix = inc.group(1).lower()
        for (tid,) in session.query(Ticket.ticket_id).all():
            if tid[:8].lower() == prefix:
                return tid

    return None


def _catalog_by_id() -> dict[str, RagCatalogEntry]:
    return {entry.ticket_id.lower(): entry for entry in iter_rag_catalog_entries()}


def _default_requester(session: Session) -> User:
    user = session.query(User).filter(User.role == "requester").first()
    if user:
        return user
    user = User(email="requester@demo.local", role="requester")
    session.add(user)
    session.flush()
    return user


def materialize_corpus_ticket(session: Session, doc_id: str) -> Optional[Ticket]:
    """Insert a single RAG/KB/enterprise corpus row when missing from SQLite."""
    canon = normalize_reference_ticket_id(doc_id)
    entry = _catalog_by_id().get(canon)
    if not entry:
        return None

    existing = session.get(Ticket, canon)
    if existing:
        return existing

    session.query(ClassificationArtifact).filter_by(ticket_id=canon).delete(
        synchronize_session=False
    )
    session.query(ResolutionArtifact).filter_by(ticket_id=canon).delete(
        synchronize_session=False
    )

    requester = _default_requester(session)
    route = (
        demo_ticket_routing(canon, entry.category, entry.hand)
        if canon.startswith("rag-") or canon.startswith("ent-")
        else None
    )
    if route:
        dept = str(route["department_queue"])
        urgency = str(route["urgency"])
        priority = str(route["priority"])
        sla_hours = int(route["sla_hours"])
        confidence = float(route["confidence"])
        escalation = bool(route["escalation_required"])
    else:
        dept = entry.department
        urgency = "medium"
        priority = "P2"
        sla_hours = 24
        confidence = 0.85
        escalation = False

    ticket = Ticket(
        ticket_id=canon,
        user_id=requester.user_id,
        title=entry.title,
        description_raw=entry.description,
        description_sanitized=entry.description,
        urgency=urgency,
        status="RESOLVED",
        hand=entry.hand,
        department_queue=dept,
        priority=priority,
        sla_hours=sla_hours,
        escalation_required=escalation,
        confidence=confidence,
    )
    session.add(ticket)

    clf = ClassificationArtifact(
        ticket_id=canon,
        use_case_category=entry.category,
        subcategory="kb_seed" if canon.startswith("kb-") else f"rag_demo_h{entry.hand}",
        confidence_hint="high" if entry.hand == "1" else "medium",
        source="rag",
    )
    session.add(clf)

    res = ResolutionArtifact(
        ticket_id=canon,
        steps_json=json.dumps(list(entry.steps)),
        citations_json=json.dumps(list(entry.citations)),
        references_json="[]",
        low_grounding=False,
        similarity_score=0.9 if entry.hand == "1" else 0.72,
    )
    session.add(res)
    session.commit()
    session.refresh(ticket)
    return ticket


def _synthetic_row_by_id() -> dict[str, dict]:
    return {row["id"].lower(): row for row in load_synthetic_raw()}


def materialize_synthetic_ticket(session: Session, doc_id: str) -> Optional[Ticket]:
    """Insert a single syn-* row from tickets_1000.json when missing from SQLite."""
    canon = doc_id.strip().lower()
    if not is_synthetic_ticket_id(canon):
        return None

    existing = session.get(Ticket, canon)
    if existing:
        return existing

    session.query(ClassificationArtifact).filter_by(ticket_id=canon).delete(
        synchronize_session=False
    )
    session.query(ResolutionArtifact).filter_by(ticket_id=canon).delete(
        synchronize_session=False
    )

    row = _synthetic_row_by_id().get(canon)
    if not row:
        return None

    requester = _default_requester(session)
    hand = str(row["hand"])
    department = canonical_department(str(row.get("department") or ""))
    if not department:
        department = department_for_category(str(row.get("category") or "Application"))

    assignee_id = None
    if hand != "1":
        from src.config.departments import department_queue_aliases

        queues = department_queue_aliases(department)
        agent = (
            session.query(User)
            .filter(User.role == "assignee", User.department.in_(list(queues)))
            .order_by(User.email.asc())
            .first()
        )
        if agent:
            assignee_id = agent.user_id

    ticket = Ticket(
        ticket_id=canon,
        user_id=requester.user_id,
        assignee_id=assignee_id,
        title=row["title"],
        description_raw=row["description"],
        description_sanitized=row["description"],
        urgency=row.get("urgency", "medium"),
        status="RESOLVED",
        hand=hand,
        department_queue=department,
        priority=row.get("priority", "P2"),
        sla_hours=int(row.get("sla_hours", 24)),
        escalation_required=hand == "3" or row.get("category") == "Security",
        confidence=0.88 if hand == "1" else 0.72 if hand == "2" else 0.42,
    )
    session.add(ticket)

    clf = ClassificationArtifact(
        ticket_id=canon,
        use_case_category=row["category"],
        subcategory=f"synthetic_h{hand}",
        confidence_hint="high" if hand == "1" else "medium" if hand == "2" else "low",
        source="rag",
    )
    session.add(clf)

    res = ResolutionArtifact(
        ticket_id=canon,
        steps_json=json.dumps(list(row.get("resolution_steps", []))),
        citations_json=json.dumps(list(row.get("citations", []))),
        references_json="[]",
        low_grounding=False,
        similarity_score=0.9 if hand == "1" else 0.72 if hand == "2" else 0.55,
    )
    session.add(res)
    session.commit()
    session.refresh(ticket)
    return ticket


def load_reference_ticket(session: Session, ticket_id: str) -> Optional[Ticket]:
    """Resolve a reference hyperlink target — DB row or materialized corpus ticket."""
    canon = resolve_reference_link(session, ticket_id)
    if not canon:
        return None

    ticket = session.get(Ticket, canon)
    if ticket:
        return ticket

    if is_corpus_ticket_id(canon):
        return materialize_corpus_ticket(session, canon)

    if is_synthetic_ticket_id(canon):
        return materialize_synthetic_ticket(session, canon)

    return None
