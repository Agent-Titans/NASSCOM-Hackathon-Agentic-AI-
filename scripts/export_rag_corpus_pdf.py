#!/usr/bin/env python3
"""Export all RAG corpus tickets to a downloadable PDF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services.rag_corpus_pdf import write_rag_corpus_pdf  # noqa: E402

_DEFAULT_OUT = ROOT / "docs" / "SAARTHI_RAG_Corpus.pdf"


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_OUT
    count = write_rag_corpus_pdf(out)
    print(f"Wrote {count} RAG entries to {out}")


if __name__ == "__main__":
    main()
