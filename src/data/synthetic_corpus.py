"""Load synthetic 1k corpus from data/synthetic/tickets_1000.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.config.departments import canonical_department
from src.data.rag_demo_corpus import RagDemoEntry

_CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "tickets_1000.json"


@lru_cache(maxsize=1)
def load_synthetic_corpus(path: Path | None = None) -> list[RagDemoEntry]:
    file_path = path or _CORPUS_PATH
    if not file_path.exists():
        return []
    data = json.loads(file_path.read_text(encoding="utf-8"))
    entries: list[RagDemoEntry] = []
    for row in data.get("tickets", []):
        entries.append(
            (
                row["id"],
                row["title"],
                row["description"],
                row["category"],
                str(row["hand"]),
                list(row["resolution_steps"]),
                list(row.get("citations", [])),
            )
        )
    return entries


def synthetic_corpus_available(path: Path | None = None) -> bool:
    file_path = path or _CORPUS_PATH
    return file_path.exists()


def synthetic_search_document(entry: RagDemoEntry) -> str:
    _id, title, description, category, hand, _steps, _cites = entry
    tier = "H1" if hand == "1" else "H2" if hand == "2" else "H3"
    return f"{title}\n{description}\n{category}\n{tier}"


def synthetic_row_metadata(row: dict[str, Any]) -> dict[str, object]:
    hand = str(row["hand"])
    return {
        "category": row["category"],
        "department": canonical_department(str(row.get("department") or "")),
        "hand": hand,
        "seed": True,
        "priority": row.get("priority", "P2"),
        "sla_hours": int(row.get("sla_hours", 24)),
        "complexity_tier": "H1" if hand == "1" else "H2" if hand == "2" else "H3",
    }


def load_synthetic_raw(path: Path | None = None) -> list[dict[str, Any]]:
    file_path = path or _CORPUS_PATH
    if not file_path.exists():
        return []
    return list(json.loads(file_path.read_text(encoding="utf-8")).get("tickets", []))
