#!/usr/bin/env python3
"""Pre-demo smoke check — golden ticket routing expectations."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.supervisor_policy import get_supervisor_policy
from src.db.session import get_session_factory, init_db
from tests.golden_runner import run_golden_set


def main() -> int:
    policy = get_supervisor_policy()
    print(f"Supervisor mode: {policy.mode}")
    init_db()
    Session = get_session_factory()
    with Session() as session:
        report = run_golden_set(session)
    for line in report.summary_lines():
        print(line)
    if not report.meets_thresholds():
        return 1
    print("\nAll golden smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
