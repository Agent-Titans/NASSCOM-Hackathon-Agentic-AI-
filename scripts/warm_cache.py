#!/usr/bin/env python3
"""Pre-warm Chroma index + persistent embedding cache (also runs at app launch)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services.retrieval_bootstrap import run_retrieval_warm  # noqa: E402


def main() -> None:
    run_retrieval_warm()
    print("Retrieval warm finished. You can also rely on automatic warm at app launch.")


if __name__ == "__main__":
    main()
