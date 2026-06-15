#!/usr/bin/env python3
"""
Clear50 — clear-title/description tickets (latency + pass rate).

  python scripts/clear50_assessment.py --live --fresh --limit 15 --delay 2.0

Output: docs/clear50_results.json, test-reports/clear50_report.html
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCENARIOS = ROOT / "data" / "set_clear50_scenarios.json"
RESULTS = ROOT / "docs" / "clear50_results.json"
REPORT = ROOT / "test-reports" / "clear50_report.html"

from scripts.master_assessment import (  # noqa: E402
    CaseSpec,
    _agent_durations,
    _agent_timing_summary,
    _build_results_payload,
    _f1_metrics,
    _hand_matches,
    _load_cases,
)


def _gemini_case_summary() -> dict[str, object]:
    from src.clients.gemini_client import GeminiClient

    return GeminiClient.eval_summary()


def _process_case(session, requester, spec: CaseSpec) -> dict:
    from src.clients.gemini_client import GeminiClient
    from src.config.departments import canonical_department
    from src.db.models import ClassificationArtifact
    from src.services.ticket_service import TicketService
    from src.stores.ticket_store import TicketStore

    GeminiClient.reset_eval_log()
    store = TicketStore(session)
    svc = TicketService(session)
    ticket = store.create(requester, spec.title, spec.description, spec.urgency)
    t0 = time.perf_counter()
    with patch.object(svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"):
        svc.process_ticket(ticket)
    elapsed = time.perf_counter() - t0
    session.refresh(ticket)
    clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket.ticket_id).first()
    hand = ticket.hand or "?"
    dept = ticket.department_queue or "?"
    hand_ok = _hand_matches(spec, hand)
    dept_ok = canonical_department(dept) == canonical_department(spec.expected_department)
    gem = _gemini_case_summary()
    return {
        "case_id": spec.case_id,
        "firm": spec.firm,
        "title": spec.title,
        "expected_hand": spec.expected_hand,
        "expected_department": spec.expected_department,
        "actual_hand": hand,
        "actual_department": dept,
        "actual_category": clf.use_case_category if clf else "?",
        "classify_source": clf.source if clf else "?",
        "latency_sec": round(elapsed, 2),
        "agent_ms": _agent_durations(session, ticket.ticket_id),
        "hand_ok": hand_ok,
        "department_ok": dept_ok,
        "pass": hand_ok and dept_ok,
        "gemini_used": gem.get("gemini_used", False),
        "gemini_models": gem.get("gemini_models", []),
        "gemini_calls_ok": gem.get("gemini_calls_ok", 0),
        "gemini_calls_failed": gem.get("gemini_calls_failed", 0),
    }


def run_live(*, fresh: bool = False, delay: float = 2.0, limit: int | None = None) -> dict[str, Any]:
    from src.db.session import get_session_factory, init_db
    from src.db.models import User

    init_db()
    specs = _load_cases(SCENARIOS)
    if limit is not None:
        specs = specs[:limit]
    existing: dict[str, dict] = {}
    if not fresh and RESULTS.exists():
        try:
            for c in json.loads(RESULTS.read_text()).get("cases", []):
                existing[c["case_id"]] = c
        except json.JSONDecodeError:
            pass

    pending = [s for s in specs if s.case_id not in existing]
    label = f"Clear{len(specs)}" if limit else "Clear50"
    print(f"=== {label}: {len(pending)} pending / {len(specs)} ===", flush=True)

    with get_session_factory()() as session:
        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            raise RuntimeError("Missing pallavi@user — run bootstrap_rag_environment.py")
        for i, spec in enumerate(pending, 1):
            if i > 1 and delay > 0:
                time.sleep(delay)
            try:
                row = _process_case(session, requester, spec)
            except Exception as exc:
                row = {
                    "case_id": spec.case_id,
                    "firm": spec.firm,
                    "title": spec.title,
                    "expected_hand": spec.expected_hand,
                    "expected_department": spec.expected_department,
                    "actual_hand": "?",
                    "actual_department": "?",
                    "actual_category": "?",
                    "classify_source": "error",
                    "latency_sec": 0,
                    "agent_ms": {},
                    "hand_ok": False,
                    "department_ok": False,
                    "pass": False,
                    "gemini_used": False,
                    "gemini_models": [],
                    "gemini_calls_ok": 0,
                    "gemini_calls_failed": 0,
                    "error": str(exc)[:200],
                }
            existing[spec.case_id] = row
            merged = [existing[k] for k in sorted(existing)]
            passed = sum(1 for r in merged if r.get("pass"))
            payload = _build_results_payload(merged, passed, len(specs), source="live")
            payload["suite"] = label
            payload["limit"] = limit
            RESULTS.write_text(json.dumps(payload, indent=2))
            mark = "PASS" if row["pass"] else "FAIL"
            models = row.get("gemini_models") or []
            gem = "yes" if row.get("gemini_used") else "no"
            print(
                f"  [{mark}] {spec.case_id} H{row['actual_hand']}/{row['actual_department']} "
                f"({row.get('classify_source','?')}) {row['latency_sec']}s "
                f"gemini={gem} models={models or '—'}",
                flush=True,
            )

    merged = [existing[k] for k in sorted(existing)]
    passed = sum(1 for r in merged if r.get("pass"))
    out = _build_results_payload(merged, passed, len(specs), source="live")
    out["suite"] = label
    out["limit"] = limit
    return out


def _latency_stats(cases: list[dict]) -> dict[str, float]:
    lat = [c["latency_sec"] for c in cases if c.get("latency_sec")]
    if not lat:
        return {"avg": 0, "p50": 0, "p90": 0, "min": 0, "max": 0}
    lat.sort()
    return {
        "avg": round(statistics.mean(lat), 2),
        "p50": round(lat[len(lat) // 2], 2),
        "p90": round(lat[int(len(lat) * 0.9)], 2),
        "min": round(min(lat), 2),
        "max": round(max(lat), 2),
    }


def _gemini_aggregate(cases: list[dict]) -> dict[str, object]:
    used = sum(1 for c in cases if c.get("gemini_used"))
    models: dict[str, int] = {}
    for c in cases:
        for m in c.get("gemini_models") or []:
            models[m] = models.get(m, 0) + 1
    return {
        "tickets_with_gemini": used,
        "tickets_without_gemini": len(cases) - used,
        "model_usage": dict(sorted(models.items(), key=lambda x: -x[1])),
    }


def _render_html(data: dict[str, Any]) -> None:
    cases = data["cases"]
    s = data["summary"]
    lat = data["latency"]
    agent = data.get("agent_timing", {})
    suite = data.get("suite", "Clear50")
    rows = "".join(
        f'<tr class="{"pass" if c.get("pass") else "fail"}"><td>{c["case_id"]}</td>'
        f'<td>{html_mod.escape(c.get("firm","")[:18])}</td>'
        f'<td>{html_mod.escape(c["title"][:45])}</td>'
        f'<td>{c["expected_department"]}</td><td>{c["actual_department"]}</td>'
        f'<td>{c.get("classify_source")}</td>'
        f'<td>{"yes" if c.get("gemini_used") else "no"}</td>'
        f'<td>{html_mod.escape(", ".join(c.get("gemini_models") or []) or "—")}</td>'
        f'<td>{c.get("latency_sec")}s</td>'
        f'<td>{"PASS" if c.get("pass") else "FAIL"}</td></tr>'
        for c in cases
    )
    agent_rows = "".join(
        f"<tr><td>{k}</td><td>{v.get('avg_ms',0)}ms</td><td>{v.get('max_ms',0)}ms</td></tr>"
        for k, v in sorted(agent.items())
        if isinstance(v, dict)
    )
    gem = data.get("gemini", {})
    gem_rows = "".join(
        f"<tr><td>{html_mod.escape(k)}</td><td>{v}</td></tr>"
        for k, v in (gem.get("model_usage") or {}).items()
    )
    doc = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>{suite} — Latency &amp; Pass Rate</title>
<style>body{{font-family:system-ui;padding:1.5rem;max-width:1100px;margin:0 auto}}
table{{border-collapse:collapse;width:100%;font-size:.8rem;margin-top:1rem}}
th,td{{border:1px solid #ddd;padding:.4rem}}tr.fail{{background:#fef2f2}}tr.pass{{background:#f0fdf4}}
.stat{{display:inline-block;margin:.5rem 1rem .5rem 0;background:#fff;border:1px solid #e2e8f0;padding:1rem;border-radius:8px}}
.num{{font-size:1.6rem;font-weight:800;color:#0d9488}}</style></head><body>
<h1>{suite} — Clear Title/Description Validation</h1>
<p>{data['evaluated_at']} · Boeing · Caterpillar · FedEx · Marriott · Pfizer · Samsung · Sony · VW · Walmart · Zoom</p>
<div class="stat"><div class="num">{s['passed']}/{s['total']}</div>Pass ({int(s['pass_rate']*100)}%)</div>
<div class="stat"><div class="num">{data['f1']['macro_f1']}</div>Macro F1</div>
<div class="stat"><div class="num">{lat['avg']}s</div>Avg latency</div>
<div class="stat"><div class="num">{lat['p50']}s</div>p50 latency</div>
<div class="stat"><div class="num">{lat['p90']}s</div>p90 latency</div>
<div class="stat"><div class="num">{gem.get('tickets_with_gemini', 0)}</div>Gemini tickets</div>
<p>Classify sources: {data['source_mix']}</p>
<p>Gemini model usage: {gem.get('model_usage', {})}</p>
<h2>Per-agent timing (avg)</h2>
<table><thead><tr><th>Agent</th><th>Avg</th><th>Max</th></tr></thead><tbody>{agent_rows}</tbody></table>
<h2>Gemini models (ticket count)</h2>
<table><thead><tr><th>Model</th><th>Tickets</th></tr></thead><tbody>{gem_rows or '<tr><td colspan=2>—</td></tr>'}</tbody></table>
<h2>Cases</h2>
<table><thead><tr><th>ID</th><th>Firm</th><th>Title</th><th>Exp</th><th>Act</th><th>Clf</th><th>Gemini</th><th>Models</th><th>Lat</th><th></th></tr></thead>
<tbody>{rows}</tbody></table>
<p style="color:#64748b;font-size:.75rem">data/set_clear50_scenarios.json · scripts/clear50_assessment.py</p>
</body></html>"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(doc, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--fresh", action="store_true")
    p.add_argument("--delay", type=float, default=2.0)
    p.add_argument("--limit", type=int, default=None, help="Run first N scenarios only (e.g. 15)")
    args = p.parse_args()

    if args.fresh:
        from scripts.clear_user_tickets import clear_user_tickets

        if RESULTS.exists():
            RESULTS.unlink()
        clear_user_tickets(reindex_chroma=True)

    if args.live or args.fresh:
        run_live(fresh=args.fresh, delay=args.delay, limit=args.limit)

    if not RESULTS.exists():
        print("No results — run with --live --fresh")
        return 1

    data = json.loads(RESULTS.read_text())
    cases = data["cases"]
    lat = _latency_stats(cases)
    src: dict[str, int] = {}
    for c in cases:
        src[c.get("classify_source", "?")] = src.get(c.get("classify_source", "?"), 0) + 1
    f1 = _f1_metrics(cases, label_key="expected_department", pred_key="actual_department")
    agent_timing = _agent_timing_summary(cases)

    out = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "suite": data.get("suite", "Clear50"),
        "limit": data.get("limit"),
        "summary": data["summary"],
        "f1": f1,
        "latency": lat,
        "agent_timing": agent_timing,
        "source_mix": src,
        "gemini": _gemini_aggregate(cases),
        "cases": cases,
    }
    RESULTS.write_text(json.dumps(out, indent=2))
    _render_html(out)

    s = data["summary"]
    suite = out.get("suite", "Clear50")
    print(f"\n=== {suite} SUMMARY ===")
    print(f"Pass: {s['passed']}/{s['total']} ({int(s['pass_rate']*100)}%)")
    print(f"Macro F1: {f1['macro_f1']}")
    print(f"Latency avg {lat['avg']}s · p50 {lat['p50']}s · p90 {lat['p90']}s")
    print(f"Sources: {src}")
    print(f"Gemini: {out['gemini']}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
