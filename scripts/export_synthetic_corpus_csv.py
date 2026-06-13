#!/usr/bin/env python3
"""Export synthetic RAG corpus to a colleague-friendly CSV."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_JSON = ROOT / "data" / "synthetic" / "tickets_1000.json"
CORPUS_CSV = ROOT / "data" / "synthetic" / "tickets_1000.csv"

COLUMNS = (
    "id",
    "title",
    "description",
    "category",
    "hand",
    "department",
    "priority",
    "sla_hours",
    "urgency",
    "resolution_steps",
    "citations",
)


def main() -> int:
    if not CORPUS_JSON.exists():
        print(f"Missing {CORPUS_JSON} — run bootstrap first", file=sys.stderr)
        return 1

    data = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
    tickets = data.get("tickets", [])
    with CORPUS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in tickets:
            out = dict(row)
            out["resolution_steps"] = " | ".join(row.get("resolution_steps") or [])
            out["citations"] = " | ".join(row.get("citations") or [])
            writer.writerow(out)

    print(f"Wrote {CORPUS_CSV} ({len(tickets)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
