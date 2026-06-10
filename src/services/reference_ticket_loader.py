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
from src.data.rag_demo_corpus import demo_ticket_routing
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket, User

_INC_REF_RE = re.compile(r"^INC-([A-F0-9]{8})$", re.I)


def normalize_reference_ticket_id(ticket_id: str) -> str:
    tid = (ticket_id or "").strip()
    if is_corpus_ticket_id(tid):
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

    return None
