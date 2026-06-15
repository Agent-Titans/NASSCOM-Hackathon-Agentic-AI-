#!/usr/bin/env python3
"""Live-routing smoke: first N Jury100 scenarios (default 10) with Gemini fallback chain."""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.jury100_assessment import SCENARIOS, _load_cases, _process_case  # noqa: E402
from scripts.master_assessment import _f1_metrics  # noqa: E402


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0

    from src.config.settings import get_settings
    from src.db.session import get_session_factory, init_db
    from src.db.models import User

    settings = get_settings()
    print("=== Gemini fallback test ===", flush=True)
    print(f"Primary classify: {settings.gemini_model_classify}", flush=True)
    print(f"Primary resolve:  {settings.gemini_model_resolve}", flush=True)
    print(f"Fallbacks:        {settings.gemini_model_fallbacks}", flush=True)
    print(f"Tickets:          {limit}", flush=True)

    init_db()
    specs = _load_cases(SCENARIOS)[:limit]
    rows: list[dict] = []

    with get_session_factory()() as session:
        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            raise RuntimeError("Missing pallavi@user — run bootstrap first")
        for i, spec in enumerate(specs, 1):
            if i > 1 and delay > 0:
                time.sleep(delay)
            row = _process_case(session, requester, spec)
            rows.append(row)
            mark = "PASS" if row["pass"] else "FAIL"
            print(
                f"  [{mark}] {spec.case_id} H{row['actual_hand']}/{row['actual_department']} "
                f"({row.get('classify_source', '?')}) {row['latency_sec']}s",
                flush=True,
            )

    passed = sum(1 for r in rows if r.get("pass"))
    lat = [r["latency_sec"] for r in rows if r.get("latency_sec")]
    f1 = _f1_metrics(rows, label_key="expected_department", pred_key="actual_department")
    src_mix: dict[str, int] = {}
    for r in rows:
        src = r.get("classify_source", "?")
        src_mix[src] = src_mix.get(src, 0) + 1

    out = {
        "suite": "fallback_smoke_10",
        "primary": settings.gemini_model_classify,
        "fallbacks": settings.gemini_model_fallbacks,
        "passed": passed,
        "total": len(rows),
        "pass_rate": round(passed / max(len(rows), 1), 3),
        "macro_f1": f1.get("macro_f1"),
        "avg_latency_sec": round(statistics.mean(lat), 2) if lat else 0,
        "classify_source_mix": src_mix,
        "cases": rows,
    }
    out_path = ROOT / "docs" / "fallback_test_10_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n=== RESULT: {passed}/{len(rows)} ({int(out['pass_rate']*100)}%) ===", flush=True)
    print(f"Macro F1: {f1.get('macro_f1')}", flush=True)
    print(f"Avg latency: {out['avg_latency_sec']}s", flush=True)
    print(f"Classify sources: {src_mix}", flush=True)
    print(f"Wrote {out_path}", flush=True)
    return 0 if passed >= len(rows) * 0.7 else 1


if __name__ == "__main__":
    raise SystemExit(main())
