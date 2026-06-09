#!/usr/bin/env python3
"""Remove every ticket and related data; reindex Chroma to RAG corpus only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
from src.services.ticket_retrieval import TicketRetrievalService  # noqa: E402

_CHILD_MODELS = (
    AuditLog,
    TicketComment,
    Feedback,
    AgentRun,
    ClassificationArtifact,
    ResolutionArtifact,
)


def reset_all_tickets(*, reindex_chroma: bool = True) -> int:
    init_db()
    Session = get_session_factory()

    with Session() as session:
        ticket_count = session.query(Ticket).count()
        if ticket_count == 0:
            print("SQLite: no tickets to remove.")
        else:
            for model in _CHILD_MODELS:
                removed = session.query(model).delete(synchronize_session=False)
                print(f"  deleted {removed} row(s) from {model.__tablename__}")
            deleted = session.query(Ticket).delete(synchronize_session=False)
            session.commit()
            print(f"SQLite: removed {deleted} ticket(s) and all related records.")

    if reindex_chroma:
        retrieval = TicketRetrievalService()
        count = retrieval.index_corpus()
        mode = getattr(retrieval.chroma, "_embedding_mode", "none")
        print(f"ChromaDB: reindexed {count} RAG corpus document(s) (mode={mode})")

    return ticket_count


if __name__ == "__main__":
    raise SystemExit(0 if reset_all_tickets() >= 0 else 1)
