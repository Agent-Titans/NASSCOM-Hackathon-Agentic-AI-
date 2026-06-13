#!/usr/bin/env python3
"""Run 10-ticket routing smoke test (first 10 from master50 suite)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCENARIOS = ROOT / "data" / "set_master50_scenarios.json"
RESULTS = ROOT / "docs" / "set_smoke10_results.json"


def main() -> int:
    from scripts.custom_25_embedding_test import _run_suite

    if not SCENARIOS.exists():
        print("Run scripts/build_master50_scenarios.py first", file=sys.stderr)
        return 1

    result = _run_suite(
        "gemini",
        reindex=False,
        scenarios_path=SCENARIOS,
        case_delay_sec=1.5,
        start_index=0,
        count=10,
        no_clear=False,
    )
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    s = result["summary"]
    print(f"SMOKE10: {s['passed']}/{s['total']} ({int(s['pass_rate'] * 100)}%)")
    for c in result["cases"]:
        ok = c.get("hand_ok") and c.get("department_ok")
        print(
            f"  [{'PASS' if ok else 'FAIL'}] {c['case_id']} "
            f"H{c['actual_hand']}/{c['actual_department']}"
        )
    return 0 if s["passed"] >= 7 else 1


if __name__ == "__main__":
    raise SystemExit(main())
