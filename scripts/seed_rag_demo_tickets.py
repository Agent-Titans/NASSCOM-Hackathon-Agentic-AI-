#!/usr/bin/env python3
"""Seed RAG demo + enterprise corpus into SQLite + ChromaDB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.enterprise_rag_corpus import ENTERPRISE_RAG_CORPUS  # noqa: E402
from src.data.rag_demo_corpus import (  # noqa: E402
    RAG_DEMO_CORPUS,
    demo_ticket_routing,
)

ALL_SEED_CORPUS = RAG_DEMO_CORPUS + ENTERPRISE_RAG_CORPUS
from src.db.models import (  # noqa: E402
    ClassificationArtifact,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.ticket_retrieval import TicketRetrievalService  # noqa: E402

_DEFAULT_REQUESTER = "requester@demo.local"


def _users_by_email(session) -> dict[str, User]:
    return {u.email: u for u in session.query(User).all()}


def seed_sqlite(session) -> int:
    users = _users_by_email(session)
    if _DEFAULT_REQUESTER not in users:
        user = User(email=_DEFAULT_REQUESTER, role="requester")
        session.add(user)
        session.commit()
        users = _users_by_email(session)

    count = 0
    for entry in ALL_SEED_CORPUS:
        doc_id, title, description, category, hand, steps, citations = entry
        route = demo_ticket_routing(doc_id, category, hand)
        dept = str(route["department_queue"])

        requester = users.get(str(route["requester_email"]), users[_DEFAULT_REQUESTER])
        assignee_email = str(route["assignee_email"])
        assignee = users.get(assignee_email) if assignee_email else None

        ticket = session.get(Ticket, doc_id)
        if ticket is None:
            ticket = Ticket(ticket_id=doc_id, user_id=requester.user_id)
            session.add(ticket)
        else:
            ticket.user_id = requester.user_id

        ticket.title = title
        ticket.description_raw = description
        ticket.description_sanitized = description
        ticket.urgency = str(route["urgency"])
        ticket.status = "RESOLVED"
        ticket.hand = hand
        ticket.department_queue = dept
        ticket.priority = str(route["priority"])
        ticket.sla_hours = int(route["sla_hours"])
        ticket.escalation_required = bool(route["escalation_required"])
        ticket.confidence = float(route["confidence"])
        ticket.assignee_id = assignee.user_id if assignee else None

        clf = (
            session.query(ClassificationArtifact)
            .filter_by(ticket_id=doc_id)
            .first()
        )
        if clf is None:
            clf = ClassificationArtifact(ticket_id=doc_id)
            session.add(clf)
        clf.use_case_category = category
        clf.subcategory = f"rag_demo_h{hand}"
        clf.confidence_hint = "high" if hand == "1" else "medium" if hand == "2" else "low"
        clf.source = "rag"

        res = (
            session.query(ResolutionArtifact)
            .filter_by(ticket_id=doc_id)
            .first()
        )
        if res is None:
            res = ResolutionArtifact(ticket_id=doc_id)
            session.add(res)
        res.steps_json = json.dumps(steps)
        res.citations_json = json.dumps(citations)
        res.low_grounding = False
        res.similarity_score = 0.9 if hand == "1" else 0.72 if hand == "2" else 0.55

        count += 1

    session.commit()
    return count


def _print_sample(session) -> None:
    print("\nSample RAG tickets (department · priority · SLA · steps):")
    for doc_id in ("rag-h1-04", "rag-h2-01", "rag-h3-09"):
        t = session.get(Ticket, doc_id)
        res = session.query(ResolutionArtifact).filter_by(ticket_id=doc_id).first()
        if not t or not res:
            continue
        steps = json.loads(res.steps_json or "[]")
        print(
            f"  {doc_id}: {t.department_queue} · {t.priority} · {t.sla_hours}h SLA · "
            f"{len(steps)} resolution steps"
        )


def main() -> None:
    init_db()
    Session = get_session_factory()

    with Session() as session:
        sqlite_count = seed_sqlite(session)
        print(f"SQLite: upserted {sqlite_count} resolved corpus tickets (demo + enterprise)")
        _print_sample(session)

    svc = TicketRetrievalService()
    chroma_count = svc.index_corpus()
    mode = getattr(svc.chroma, "_embedding_mode", "none")
    print(f"ChromaDB: indexed {chroma_count} documents (embedding={mode})")

    tests = [
        ("Hand 1", "I forgot my password and cannot login to portal"),
        ("Hand 2", "Getting page not found 401 error unable to access this page"),
        ("Hand 3", "Duplicate issues from upstream data quality problem"),
    ]
    with Session() as session:
        for label, text in tests:
            match = svc.find_similar(session, text)
            if match:
                print(
                    f"  {label} match: {match.ticket_id} "
                    f"→ {match.department_queue} "
                    f"({match.classification.use_case_category}, "
                    f"score={match.similarity_score:.2f})"
                )
            else:
                print(f"  {label} match: NONE")


if __name__ == "__main__":
    main()
