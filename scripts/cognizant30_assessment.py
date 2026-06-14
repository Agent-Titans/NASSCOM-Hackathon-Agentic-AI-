#!/usr/bin/env python3
"""
Cognizant30 assessment — 30 Cognizant Technology Services routing scenarios.

  python scripts/cognizant30_assessment.py              # cached + report
  python scripts/cognizant30_assessment.py --live       # live run (~7 min)
  python scripts/cognizant30_assessment.py --live --fresh

Output: test-reports/cognizant30_report.html, docs/cognizant30_results.json
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCENARIOS = ROOT / "data" / "set_cognizant30_scenarios.json"
RESULTS_JSON = ROOT / "docs/cognizant30_results.json"
REPORT_HTML = ROOT / "test-reports/cognizant30_report.html"

PIPELINE_AGENTS = (
    "guardrail",
    "retrieval",
    "classifier",
    "router",
    "resolver",
    "supervisor",
    "resolution_format",
)


@dataclass
class CaseSpec:
    case_id: str
    title: str
    description: str
    expected_hand: str
    expected_department: str
    expected_category: Optional[str] = None
    urgency: str = "medium"
    acceptable_hands: Optional[tuple[str, ...]] = None
    notes: str = ""
    firm: str = ""


def _load_cases(path: Path = SCENARIOS) -> list[CaseSpec]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[CaseSpec] = []
    for row in data["cases"]:
        exp = row.get("expect", {})
        out.append(
            CaseSpec(
                case_id=row["id"],
                title=row["title"],
                description=row["description"],
                expected_hand=str(exp.get("hand", "2")),
                expected_department=str(exp.get("department", "Application")),
                expected_category=str(exp.get("category")) if exp.get("category") else None,
                urgency=row.get("urgency", "medium"),
                acceptable_hands=tuple(row["acceptable_hands"]) if row.get("acceptable_hands") else None,
                notes=row.get("notes", ""),
                firm=row.get("firm", "Cognizant"),
            )
        )
    return out


def _hand_matches(spec: CaseSpec, hand: str) -> bool:
    if spec.acceptable_hands:
        return hand in spec.acceptable_hands
    return hand == spec.expected_hand


def _agent_durations(session, ticket_id: str) -> dict[str, int]:
    from src.db.models import AuditLog

    rows = (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.event_type == "agent_completed",
        )
        .all()
    )
    out: dict[str, int] = {}
    for row in rows:
        if row.agent and row.duration_ms is not None:
            out[row.agent] = int(row.duration_ms)
    return out


def _process_case(session, requester, spec: CaseSpec) -> dict:
    from src.config.departments import canonical_department
    from src.db.models import ClassificationArtifact
    from src.services.ticket_service import TicketService
    from src.stores.ticket_store import TicketStore

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
    category = clf.use_case_category if clf else "?"
    hand_ok = _hand_matches(spec, hand)
    dept_ok = canonical_department(dept) == canonical_department(spec.expected_department)
    cat_ok = (not spec.expected_category) or category == spec.expected_category
    return {
        "case_id": spec.case_id,
        "firm": spec.firm,
        "title": spec.title,
        "description": spec.description[:120],
        "expected_hand": spec.expected_hand,
        "expected_department": spec.expected_department,
        "expected_category": spec.expected_category or "",
        "actual_hand": hand,
        "actual_department": dept,
        "actual_category": category,
        "classify_source": clf.source if clf else "?",
        "status": ticket.status or "?",
        "latency_sec": round(elapsed, 2),
        "agent_ms": _agent_durations(session, ticket.ticket_id),
        "hand_ok": hand_ok,
        "department_ok": dept_ok,
        "category_ok": cat_ok,
        "pass": hand_ok and dept_ok,
        "notes": spec.notes,
    }


def _f1_metrics(cases: list[dict], *, label_key: str, pred_key: str) -> dict[str, Any]:
    labels = sorted(
        {c[label_key] for c in cases if c.get(label_key)}
        | {c[pred_key] for c in cases if c.get(pred_key)}
    )
    per_label: dict[str, dict[str, float]] = {}
    tp = fp = fn = 0
    for lab in labels:
        t = sum(1 for c in cases if c.get(label_key) == lab and c.get(pred_key) == lab)
        p = sum(1 for c in cases if c.get(pred_key) == lab)
        e = sum(1 for c in cases if c.get(label_key) == lab)
        prec = t / p if p else 0.0
        rec = t / e if e else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
        per_label[lab] = {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3), "support": e}
        tp += t
        fp += p - t
        fn += e - t
    micro_p = tp / (tp + fp) if (tp + fp) else 0.0
    micro_r = tp / (tp + fn) if (tp + fn) else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0
    macro_f1 = sum(v["f1"] for v in per_label.values()) / max(len(per_label), 1)
    return {"macro_f1": round(macro_f1, 3), "micro_f1": round(micro_f1, 3), "per_label": per_label}


def _agent_timing_summary(cases: list[dict]) -> dict[str, Any]:
    totals: dict[str, list[int]] = defaultdict(list)
    for c in cases:
        for agent, ms in (c.get("agent_ms") or {}).items():
            totals[agent].append(ms)
    summary: dict[str, Any] = {}
    grand = 0
    for agent in PIPELINE_AGENTS:
        vals = totals.get(agent, [])
        if not vals:
            continue
        avg = int(sum(vals) / len(vals))
        summary[agent] = {"avg_ms": avg, "max_ms": max(vals), "samples": len(vals)}
        grand += avg
    summary["_pipeline_avg_ms"] = grand
    return summary


def run_live_routing(delay: float = 0.6, *, fresh: bool = False) -> dict[str, Any]:
    from src.db.session import get_session_factory, init_db
    from src.db.models import User

    init_db()
    specs = _load_cases()
    existing: dict[str, dict] = {}
    if not fresh and RESULTS_JSON.exists():
        try:
            for c in json.loads(RESULTS_JSON.read_text()).get("cases", []):
                existing[c["case_id"]] = c
        except json.JSONDecodeError:
            pass

    pending = [s for s in specs if s.case_id not in existing]
    print(f"  {len(pending)} pending of {len(specs)} cases", flush=True)

    with get_session_factory()() as session:
        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            raise RuntimeError("Missing pallavi@user")
        for i, spec in enumerate(pending, 1):
            if i > 1 and delay > 0:
                time.sleep(delay)
            row = _process_case(session, requester, spec)
            existing[spec.case_id] = row
            merged = [existing[k] for k in sorted(existing)]
            passed = sum(1 for r in merged if r.get("pass"))
            payload = {
                "summary": {
                    "total": len(specs),
                    "passed": passed,
                    "pass_rate": round(passed / len(specs), 3),
                    "source": "live",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                },
                "cases": merged,
            }
            RESULTS_JSON.write_text(json.dumps(payload, indent=2))
            mark = "PASS" if row["pass"] else "FAIL"
            print(
                f"  [{mark}] {spec.case_id}: H{row['actual_hand']}/{row['actual_department']} "
                f"({row.get('classify_source','?')}) {row['latency_sec']}s",
                flush=True,
            )

    merged = [existing[k] for k in sorted(existing)]
    passed = sum(1 for r in merged if r.get("pass"))
    return {
        "total": len(specs),
        "passed": passed,
        "pass_rate": round(passed / len(specs), 3),
        "source": "live",
        "cases": merged,
    }


def _render_html(
    *,
    summary: dict,
    cases: list[dict],
    f1_dept: dict,
    timing: dict,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = summary.get("total", 30)
    passed = summary.get("passed", 0)
    rate = summary.get("pass_rate", 0)
    avg_lat = round(sum(c.get("latency_sec", 0) for c in cases) / max(len(cases), 1), 2)
    kw = sum(1 for c in cases if c.get("classify_source") == "keyword")
    fails = [c for c in cases if not c.get("pass")]

    cat_stats: dict[str, dict] = defaultdict(lambda: {"pass": 0, "total": 0})
    for c in cases:
        k = c.get("expected_category") or c.get("expected_department", "?")
        cat_stats[k]["total"] += 1
        if c.get("pass"):
            cat_stats[k]["pass"] += 1

    cat_rows = "".join(
        f"<tr><td>{html_mod.escape(cat)}</td><td>{s['pass']}/{s['total']}</td>"
        f"<td><strong>{int(100*s['pass']/max(s['total'],1))}%</strong></td></tr>"
        for cat, s in sorted(cat_stats.items())
    )

    timing_rows = "".join(
        f'<tr><td>{html_mod.escape(a)}</td><td>{info["avg_ms"]} ms</td>'
        f'<td>{info["max_ms"]} ms</td></tr>'
        for a, info in timing.items()
        if not a.startswith("_")
    )

    f1_rows = "".join(
        f'<tr><td>{html_mod.escape(lab)}</td><td>{m["f1"]}</td><td>{m["support"]}</td></tr>'
        for lab, m in sorted(f1_dept.get("per_label", {}).items())
    )

    case_rows = []
    for c in cases:
        cls = "pass" if c.get("pass") else "fail"
        badge = "PASS" if c.get("pass") else "FAIL"
        case_rows.append(
            f'<tr class="{cls}"><td>{c["case_id"]}</td>'
            f'<td><strong>{html_mod.escape(c["title"][:50])}</strong></td>'
            f'<td>H{c["expected_hand"]}→H{c["actual_hand"]}</td>'
            f'<td>{html_mod.escape(c["expected_department"])}→{html_mod.escape(c["actual_department"])}</td>'
            f'<td>{html_mod.escape(c.get("classify_source","?"))}</td>'
            f'<td>{c.get("latency_sec")}s</td>'
            f'<td><span class="badge {cls}">{badge}</span></td></tr>'
        )

    fail_rows = "".join(
        f'<tr><td>{c["case_id"]}</td><td>{html_mod.escape(c["title"][:45])}</td>'
        f'<td>{html_mod.escape(c["expected_department"])}</td>'
        f'<td>{html_mod.escape(c["actual_department"])}</td></tr>'
        for c in fails
    ) or '<tr><td colspan="4">All 30 passed</td></tr>'

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAARTHI Cognizant30 Report</title>
<style>
:root{{--pass:#0d7a3e;--fail:#c0392b;--accent:#0f766e;--bg:#f4f6f8;--card:#fff;--border:#dde3ea}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:var(--bg);color:#1a1a2e;padding:2rem;line-height:1.5}}
.header{{background:linear-gradient(135deg,#1e40af,#0f766e,#0d9488);color:#fff;padding:2.5rem;border-radius:14px;margin-bottom:1.5rem}}
.header h1{{font-size:2rem;margin-bottom:.5rem}}
.stats{{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem 1.3rem;min-width:110px}}
.stat .num{{font-size:1.7rem;font-weight:700;color:var(--accent)}}
.stat .lbl{{font-size:.7rem;color:#666;text-transform:uppercase}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem}}
@media(max-width:900px){{.grid2{{grid-template-columns:1fr}}}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.4rem;margin-bottom:1.5rem}}
.card h2{{font-size:1.1rem;margin-bottom:1rem;color:var(--accent)}}
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{background:var(--accent);color:#fff;padding:.55rem .7rem;text-align:left}}
td{{padding:.5rem .7rem;border-bottom:1px solid var(--border);vertical-align:top}}
tr.pass td{{background:#f0faf4}} tr.fail td{{background:#fef5f4}}
.badge{{padding:.12rem .4rem;border-radius:4px;font-size:.68rem;font-weight:700}}
.badge.pass{{background:#d4edda;color:var(--pass)}} .badge.fail{{background:#f8d7da;color:var(--fail)}}
.footer{{margin-top:2rem;font-size:.78rem;color:#888}}
</style></head><body>
<div class="header">
<h1>SAARTHI — Cognizant30 Assessment</h1>
<p>Cognizant Technology Services · 30 delivery scenarios · {ts}</p>
</div>
<div class="stats">
<div class="stat"><div class="num">{passed}/{total}</div><div class="lbl">Routing pass</div></div>
<div class="stat"><div class="num">{int(rate*100)}%</div><div class="lbl">Pass rate</div></div>
<div class="stat"><div class="num">{f1_dept.get("macro_f1",0)}</div><div class="lbl">Dept macro-F1</div></div>
<div class="stat"><div class="num">{avg_lat}s</div><div class="lbl">Avg latency</div></div>
<div class="stat"><div class="num">{kw}</div><div class="lbl">Keyword short-circuit</div></div>
</div>
<div class="grid2">
<div class="card"><h2>Pass rate by category</h2>
<table><thead><tr><th>Category</th><th>Pass</th><th>Rate</th></tr></thead><tbody>{cat_rows}</tbody></table></div>
<div class="card"><h2>Department F1</h2>
<table><thead><tr><th>Department</th><th>F1</th><th>N</th></tr></thead><tbody>{f1_rows}</tbody></table></div>
</div>
<div class="card"><h2>Per-agent avg duration</h2>
<table><thead><tr><th>Agent</th><th>Avg</th><th>Max</th></tr></thead><tbody>{timing_rows}</tbody></table></div>
<div class="card"><h2>Failures ({len(fails)})</h2>
<table><thead><tr><th>ID</th><th>Title</th><th>Expected</th><th>Actual</th></tr></thead><tbody>{fail_rows}</tbody></table></div>
<h2 style="margin-bottom:.6rem">30 scenario results</h2>
<table><thead><tr><th>ID</th><th>Title</th><th>Hand</th><th>Dept</th><th>Classify</th><th>Latency</th><th></th></tr></thead>
<tbody>{"".join(case_rows)}</tbody></table>
<p class="footer">data/set_cognizant30_scenarios.json · python scripts/cognizant30_assessment.py --live</p>
</body></html>"""
    REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    REPORT_HTML.write_text(doc, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--fresh", action="store_true")
    args = p.parse_args()

    if args.live or args.fresh or not RESULTS_JSON.exists():
        print("=== Live Cognizant30 routing ===", flush=True)
        summary = run_live_routing(delay=0.6, fresh=args.fresh)
        cases = summary.get("cases", [])
    else:
        data = json.loads(RESULTS_JSON.read_text())
        summary = data.get("summary", {})
        cases = data.get("cases", [])
        print(f"=== Cached Cognizant30: {summary.get('passed')}/{summary.get('total')} ===")

    rate = summary.get("pass_rate", 0)
    f1_dept = _f1_metrics(cases, label_key="expected_department", pred_key="actual_department")
    timing = _agent_timing_summary(cases)

    payload = {
        "summary": {**summary, "macro_f1": f1_dept.get("macro_f1")},
        "f1_department": f1_dept,
        "agent_timing": timing,
        "cases": cases,
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2))

    _render_html(summary=summary, cases=cases, f1_dept=f1_dept, timing=timing)
    print(f"\n=== Cognizant30: {summary.get('passed')}/{summary.get('total')} ({int(rate*100)}%) ===")
    print(f"Dept macro-F1: {f1_dept.get('macro_f1')}")
    print(f"Report: {REPORT_HTML}")
    return 0 if rate >= 0.85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
