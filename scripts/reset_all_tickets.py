#!/usr/bin/env python3
"""Remove every ticket and related data; optionally wipe Chroma to empty."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.settings import get_settings  # noqa: E402
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

_CHILD_MODELS = (
    AuditLog,
    TicketComment,
    Feedback,
    AgentRun,
    ClassificationArtifact,
    ResolutionArtifact,
)


def _clear_sqlite_tickets() -> int:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        ticket_count = session.query(Ticket).count()
        if ticket_count == 0:
            print("SQLite: no tickets to remove.")
            return 0
        for model in _CHILD_MODELS:
            removed = session.query(model).delete(synchronize_session=False)
            print(f"  deleted {removed} row(s) from {model.__tablename__}")
        deleted = session.query(Ticket).delete(synchronize_session=False)
        session.commit()
        print(f"SQLite: removed {deleted} ticket(s) and all related records.")
        return deleted


def _clear_chroma_empty() -> None:
    settings = get_settings()
    chroma_dir = Path(settings.chroma_persist_dir)
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print(f"ChromaDB: removed {chroma_dir}")
    else:
        print("ChromaDB: already empty (no data/chroma directory).")

    cache_path = settings.embedding_cache_path
    if cache_path.exists():
        cache_path.write_text("{}", encoding="utf-8")
        print(f"Embedding cache: cleared {cache_path.name}")


def _reindex_chroma_corpus() -> int:
    from src.services.ticket_retrieval import TicketRetrievalService

    retrieval = TicketRetrievalService()
    count = retrieval.index_corpus()
    mode = getattr(retrieval.chroma, "_embedding_mode", "none")
    print(f"ChromaDB: reindexed {count} RAG corpus document(s) (mode={mode})")
    return count


def reset_all_tickets(*, reindex_chroma: bool = True) -> int:
    removed = _clear_sqlite_tickets()
    if reindex_chroma:
        _reindex_chroma_corpus()
    else:
        _clear_chroma_empty()
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset tickets and optional Chroma state.")
    parser.add_argument(
        "--empty",
        action="store_true",
        help="Wipe all SQLite tickets and leave Chroma/corpus at zero (no re-seed).",
    )
    args = parser.parse_args()
    reset_all_tickets(reindex_chroma=not args.empty)
    if args.empty:
        print(
            "Empty slate: set RAG_AUTO_SEED=false in .env so the app does not "
            "auto-load corpus on startup. Run seed_rag_demo_tickets.py when ready."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
