#!/usr/bin/env python3
"""
Remove user-submitted tickets from SQLite; keep RAG seed corpus (syn-*, KB).

When reindex_chroma=True (assessment --fresh):
  - Deletes live-ticket vectors from Chroma only (does NOT wipe 1k syn-* index).
  - Rebuilds full synthetic Chroma from tickets_1000.json if corpus count is low.
"""
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
from src.services.process_cache import invalidate_process_caches  # noqa: E402
from src.services.ticket_retrieval import (  # noqa: E402
    TicketRetrievalService,
    _is_corpus_id,
)
from src.stores.chroma_store import ChromaTicketStore  # noqa: E402

_MIN_HEALTHY_CHROMA = 100


def _seed_ticket_ids() -> set[str]:
    return {entry[0] for entry in RAG_DEMO_CORPUS + ENTERPRISE_RAG_CORPUS}


def _purge_user_chroma_vectors() -> tuple[int, int]:
    """Remove live-assessment UUID vectors; keep syn-*, rag-*, kb-*, ent-*."""
    chroma = ChromaTicketStore()
    if not chroma.available or not chroma._collection:
        return 0, chroma.count

    col = chroma._collection
    all_ids = col.get(include=[])["ids"]
    user_ids = [
        doc_id
        for doc_id in all_ids
        if not _is_corpus_id(doc_id) and not str(doc_id).startswith("syn-")
    ]
    if user_ids:
        batch = 100
        for start in range(0, len(user_ids), batch):
            col.delete(ids=user_ids[start : start + batch])
    invalidate_process_caches()
    return len(user_ids), chroma.count


def _rebuild_chroma_from_synthetic() -> int:
    """Full Chroma rebuild: KB seeds + 1k synthetic (same as bootstrap ingest)."""
    from scripts.ingest_synthetic_corpus import _load_tickets, build_chroma_entries
    from src.config.settings import get_settings

    settings = get_settings()
    tickets = _load_tickets(settings.synthetic_corpus_path)
    if not tickets:
        return 0
    svc = TicketRetrievalService()
    return svc.index_synthetic_chroma(build_chroma_entries(tickets))


def _sync_chroma_after_user_cleanup() -> int:
    """Purge user vectors; rebuild synthetic index if corpus was truncated."""
    removed, remaining = _purge_user_chroma_vectors()
    if removed:
        print(f"ChromaDB: purged {removed} live ticket vector(s); {remaining} corpus docs remain")
    if remaining < _MIN_HEALTHY_CHROMA:
        print(f"ChromaDB: corpus low ({remaining}) — rebuilding from synthetic JSON…")
        count = _rebuild_chroma_from_synthetic()
        print(f"ChromaDB: rebuilt {count} corpus documents")
        return count
    if not removed:
        print(f"ChromaDB: {remaining} corpus documents (no user vectors to purge)")
    return remaining


def clear_user_tickets(*, reindex_chroma: bool = True) -> int:
    init_db()
    seed_ids = _seed_ticket_ids()
    Session = get_session_factory()
    deleted = 0

    with Session() as session:
        user_ticket_ids = [
            tid
            for (tid,) in session.query(Ticket.ticket_id).all()
            if tid not in seed_ids and not _is_corpus_id(tid)
        ]
        if not user_ticket_ids:
            print("No user-submitted tickets to remove.")
        else:
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
        _sync_chroma_after_user_cleanup()

    if deleted:
        print(f"Removed {deleted} user-submitted ticket(s). Seed corpus preserved.")
    return deleted


if __name__ == "__main__":
    raise SystemExit(0 if clear_user_tickets() >= 0 else 1)
