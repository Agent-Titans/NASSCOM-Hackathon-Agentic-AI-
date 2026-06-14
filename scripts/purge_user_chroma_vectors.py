#!/usr/bin/env python3
"""Remove user-submitted ticket vectors from Chroma; keep KB/RAG/syn-* corpus."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services.process_cache import invalidate_process_caches  # noqa: E402
from src.services.ticket_retrieval import _is_corpus_id  # noqa: E402
from src.stores.chroma_store import ChromaTicketStore  # noqa: E402


def main() -> int:
    chroma = ChromaTicketStore()
    if not chroma.available:
        print("Chroma not available — nothing to purge.")
        return 0

    col = chroma._collection
    all_ids = col.get(include=[])["ids"]
    user_ids = [
        doc_id
        for doc_id in all_ids
        if not _is_corpus_id(doc_id) and not doc_id.startswith("syn-")
    ]
    print(f"Chroma total: {len(all_ids)}")
    print(f"User vectors to remove: {len(user_ids)}")
    if user_ids:
        batch = 100
        for start in range(0, len(user_ids), batch):
            col.delete(ids=user_ids[start : start + batch])
        print(f"Removed {len(user_ids)} user ticket vector(s) from Chroma.")
    else:
        print("No user ticket vectors in Chroma.")

    print(f"Chroma remaining: {chroma.count}")
    invalidate_process_caches()
    print("Process caches invalidated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
