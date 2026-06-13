#!/usr/bin/env python3
"""Generate data/synthetic/tickets_1000.json for RAG ingest."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.synthetic_corpus_generator import DEFAULT_OUTPUT, write_corpus  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic ticket corpus JSON.")
    parser.add_argument("--count", type=int, default=1000, help="Number of tickets")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out = write_corpus(args.output, count=args.count)
    print(f"Generated {args.count} tickets → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
