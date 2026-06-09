"""Enterprise RAG corpus — 30 supervised tickets (15 H1 self-help, 15 H2 engineering)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from src.data.rag_demo_corpus import RagDemoEntry

_CORPUS_PATH = Path(__file__).resolve().parent / "enterprise_rag_corpus.json"
_TIER_TO_HAND = {"H1": "1", "H2": "2", "H3": "3"}


@lru_cache(maxsize=1)
def load_enterprise_corpus() -> list[RagDemoEntry]:
    """Load JSON corpus; complexity_tier H1/H2 maps to source_hand 1/2."""
    raw = json.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
    entries: list[RagDemoEntry] = []
    for row in raw:
        hand = _TIER_TO_HAND.get(row["complexity_tier"], "2")
        cite = f"ENT-{row['complexity_tier']}-{row['id'].split('-')[-1].upper()}"
        entries.append(
            (
                row["id"],
                row["title"],
                row["issue_description"],
                row["category"],
                hand,
                list(row["resolution_steps"]),
                [cite, row["id"]],
            )
        )
    return entries


def enterprise_search_document(entry: RagDemoEntry) -> str:
    """Indexed text for Chroma / keyword retrieval."""
    _id, title, description, category, hand, _steps, _cites = entry
    tier = "H1" if hand == "1" else "H2" if hand == "2" else "H3"
    return f"{title}\n{description}\n{category}\n{tier}"


ENTERPRISE_RAG_CORPUS: list[RagDemoEntry] = load_enterprise_corpus()
