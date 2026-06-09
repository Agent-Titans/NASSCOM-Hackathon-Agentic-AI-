#!/usr/bin/env python3
"""Index resolved tickets + KB seeds into ChromaDB."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.ticket_retrieval import TicketRetrievalService  # noqa: E402


def main() -> None:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        svc = TicketRetrievalService()
        count = svc.index_corpus()
        if count == 0:
            svc.ensure_index(session)
            count = svc.chroma.count
        print(f"Chroma indexed documents: {count}")


if __name__ == "__main__":
    main()
