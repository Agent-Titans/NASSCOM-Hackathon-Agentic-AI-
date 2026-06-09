#!/usr/bin/env python3
"""Remove user-submitted tickets from SQLite; keep RAG seed corpus tickets."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.enterprise_rag_corpus import ENTERPRISE_RAG_CORPUS  # noqa: E402
from src.data.rag_demo_corpus import RAG_DEMO_CORPUS  # noqa: E402
from src.db.models import (  # noqa: E402
    AgentRun,
    AuditLog,
    ClassificationArtifact,
    Feedback,
    ResolutionArtifact,
    Ticket,
    TicketComment,
)
from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.ticket_retrieval import (  # noqa: E402
    TicketRetrievalService,
    _is_corpus_id,
)


def _seed_ticket_ids() -> set[str]:
    return {entry[0] for entry in RAG_DEMO_CORPUS + ENTERPRISE_RAG_CORPUS}


def clear_user_tickets(*, reindex_chroma: bool = True) -> int:
    init_db()
    seed_ids = _seed_ticket_ids()
    Session = get_session_factory()

    with Session() as session:
        user_ticket_ids = [
            tid
            for (tid,) in session.query(Ticket.ticket_id).all()
            if tid not in seed_ids and not _is_corpus_id(tid)
        ]
        if not user_ticket_ids:
            print("No user-submitted tickets to remove.")
            return 0

        for model, col in (
            (AuditLog, AuditLog.ticket_id),
            (TicketComment, TicketComment.ticket_id),
            (Feedback, Feedback.ticket_id),
            (AgentRun, AgentRun.ticket_id),
            (ClassificationArtifact, ClassificationArtifact.ticket_id),
            (ResolutionArtifact, ResolutionArtifact.ticket_id),
        ):
            session.query(model).filter(col.in_(user_ticket_ids)).delete(
                synchronize_session=False
            )

        deleted = (
            session.query(Ticket)
            .filter(Ticket.ticket_id.in_(user_ticket_ids))
            .delete(synchronize_session=False)
        )
        session.commit()

    if reindex_chroma:
        retrieval = TicketRetrievalService()
        count = retrieval.index_corpus()
        print(f"ChromaDB: reindexed {count} corpus documents")

    print(f"Removed {deleted} user-submitted ticket(s). Seed corpus preserved.")
    return deleted


if __name__ == "__main__":
    raise SystemExit(0 if clear_user_tickets() >= 0 else 1)
