#!/usr/bin/env python3
"""Run master 100 routing test with incremental saves."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCENARIOS = ROOT / "data" / "set_master100_scenarios.json"
RESULTS = ROOT / "docs" / "set_master100_results.json"


def main() -> int:
    from scripts.custom_25_embedding_test import _run_suite

    if not SCENARIOS.exists():
        print("Run scripts/build_master100_scenarios.py first", file=sys.stderr)
        return 1

    existing_cases = None
    if RESULTS.exists():
        existing_cases = json.loads(RESULTS.read_text()).get("cases")
        print(f"Resuming from {len(existing_cases or [])} existing results")

    start = len(existing_cases or [])
    for idx in range(start, 100):
        print(f"--- {idx + 1}/100 ---", flush=True)
        result = _run_suite(
            "gemini",
            reindex=False,
            scenarios_path=SCENARIOS,
            case_delay_sec=2.0 if idx > 0 else 0,
            start_index=idx,
            count=1,
            no_clear=(idx > 0),
            existing_cases=existing_cases,
        )
        existing_cases = result["cases"]
        RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
        c = result["cases"][-1]
        ok = c.get("hand_ok") and c.get("department_ok")
        print(
            f"  [{ 'PASS' if ok else 'FAIL' }] {c['case_id']} "
            f"H{c['actual_hand']}/{c['actual_department']} "
            f"({result['summary']['passed']}/{result['summary']['total']})",
            flush=True,
        )

    s = result["summary"]
    print(
        f"DONE {s['passed']}/{s['total']} ({int(s['pass_rate'] * 100)}%)",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
