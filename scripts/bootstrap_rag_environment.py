#!/usr/bin/env python3
"""
Clean slate + seed users + 1k synthetic RAG corpus.

  1. Wipe live tickets (keeps users)
  2. Wipe Chroma + embedding cache
  3. Seed users / assignees for all Use Case departments
  4. Generate tickets_1000.json if missing
  5. Ingest into SQLite (RESOLVED) + Chroma
  6. Warm embedding disk cache (optional)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _run(cmd: list[str]) -> None:
    print(f"\n→ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap clean RAG environment.")
    parser.add_argument("--skip-warm", action="store_true", help="Skip embedding warm_cache")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument(
        "--regenerate-corpus",
        action="store_true",
        help="Regenerate tickets_1000.json (default: keep committed corpus)",
    )
    args = parser.parse_args()

    py = sys.executable
    corpus = ROOT / "data" / "synthetic" / "tickets_1000.json"

    # Clear live tickets only (not users)
    from scripts.reset_all_tickets import _clear_chroma_empty, _clear_sqlite_tickets  # noqa: E402

    removed = _clear_sqlite_tickets()
    _clear_chroma_empty()
    print(f"Cleared {removed} live ticket(s) and Chroma state.")

    _run([py, str(ROOT / "scripts" / "seed_users.py")])
    if args.regenerate_corpus or not corpus.exists():
        _run(
            [
                py,
                str(ROOT / "scripts" / "generate_synthetic_corpus.py"),
                "--count",
                str(args.count),
            ]
        )
    else:
        print(f"\n→ Using existing corpus {corpus}")

    patch = ROOT / "scripts" / "patch_rag_assignee_titles.py"
    if patch.exists():
        _run([py, str(patch)])

    _run([py, str(ROOT / "scripts" / "ingest_synthetic_corpus.py")])

    if not args.skip_warm:
        warm = ROOT / "scripts" / "warm_cache.py"
        if warm.exists():
            _run([py, str(warm)])

    csv_export = ROOT / "scripts" / "export_synthetic_corpus_csv.py"
    if csv_export.exists():
        _run([py, str(csv_export)])

    print(
        "\n✓ RAG environment ready.\n"
        "  Live ticket table is empty — create new tickets via the UI.\n"
        "  1,000 RESOLVED syn-* tickets in SQLite + Chroma (Gemini embeddings).\n"
        "  Set RAG_AUTO_SEED=false and RAG_CORPUS_MODE=synthetic in .env.\n"
        "  RAG_EMBEDDING_BACKEND=gemini (default) — matches routing test reports.\n"
        "  Gemini API key required for classify, resolve, and embed on new tickets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
