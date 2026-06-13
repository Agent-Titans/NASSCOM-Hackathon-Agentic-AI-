#!/usr/bin/env python3
"""Remove live UI tickets only — keeps syn-* RAG history + Chroma index."""
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
from src.services.process_cache import invalidate_retrieval_cache  # noqa: E402
from src.stores.chroma_store import ChromaTicketStore  # noqa: E402


def clean_live_tickets() -> int:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        live_ids = [
            tid
            for (tid,) in session.query(Ticket.ticket_id)
            .filter(~Ticket.ticket_id.like("syn-%"))
            .all()
        ]
        if not live_ids:
            print("No live UI tickets to remove.")
            return 0

        for model, col in (
            (AuditLog, AuditLog.ticket_id),
            (TicketComment, TicketComment.ticket_id),
            (Feedback, Feedback.ticket_id),
            (AgentRun, AgentRun.ticket_id),
            (ClassificationArtifact, ClassificationArtifact.ticket_id),
            (ResolutionArtifact, ResolutionArtifact.ticket_id),
        ):
            session.query(model).filter(col.in_(live_ids)).delete(synchronize_session=False)

        deleted = (
            session.query(Ticket)
            .filter(Ticket.ticket_id.in_(live_ids))
            .delete(synchronize_session=False)
        )
        session.commit()

    invalidate_retrieval_cache()
    return deleted


def main() -> int:
    removed = clean_live_tickets()
    chroma = ChromaTicketStore()
    Session = get_session_factory()
    with Session() as session:
        syn = session.query(Ticket).filter(Ticket.ticket_id.like("syn-%")).count()
        live = session.query(Ticket).filter(~Ticket.ticket_id.like("syn-%")).count()

    print(f"Removed {removed} live ticket(s).")
    print(f"SQLite: {syn} syn-* (RAG) · {live} live UI tickets")
    print(f"Chroma: {chroma.count} documents (mode={chroma._embedding_mode})")
    print("\nReady for UI demo — restart Streamlit if it is running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
