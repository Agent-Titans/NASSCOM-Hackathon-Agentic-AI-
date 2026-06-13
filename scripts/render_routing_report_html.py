#!/usr/bin/env python3
"""Render routing test results as HTML report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_rows(scenarios: dict, results: dict) -> list[dict]:
    result_map = {c["case_id"]: c for c in results["cases"]}
    rows = []
    for case in scenarios["cases"]:
        cid = case["id"]
        r = result_map.get(cid, {})
        passed = r.get("department_ok", False) and r.get("hand_ok", False)
        actual_dept = r.get("actual_department", "—")
        expected_dept = case["expect"]["department"]
        specialist_path = "—"
        if not passed:
            specialist_path = (
                f"Agent → SecOps Routing Specialists → {expected_dept}"
            )
        rows.append({
            "id": cid,
            "firm": case.get("firm", "—"),
            "title": case["title"],
            "description": case["description"],
            "expected_hand": case["expect"]["hand"],
            "expected_dept": expected_dept,
            "actual_hand": r.get("actual_hand", "—"),
            "actual_dept": actual_dept,
            "specialist_path": specialist_path,
            "passed": passed,
        })
    return rows


def _firm_stats(rows: list[dict]) -> list[tuple[str, int, int, int]]:
    buckets: dict[str, list[bool]] = {}
    for row in rows:
        firm = row.get("firm") or "—"
        buckets.setdefault(firm, []).append(row["passed"])
    stats = []
    for firm in sorted(buckets):
        results = buckets[firm]
        total = len(results)
        passed = sum(1 for ok in results if ok)
        pct = round(100 * passed / total) if total else 0
        stats.append((firm, passed, total, pct))
    return stats


def render_html(
    title: str,
    subtitle: str,
    rows: list[dict],
    outfile: Path,
    accent: str = "#0070ad",
) -> tuple[int, int]:
    total = len(rows)
    pass_count = sum(1 for r in rows if r["passed"])
    fail = total - pass_count
    pct = round(100 * pass_count / total) if total else 0
    specialist_rows = [r for r in rows if not r["passed"]]
    has_firm = any(r.get("firm") and r["firm"] != "—" for r in rows)
    firm_stats = _firm_stats(rows) if has_firm else []
    firm_rows = []
    for firm, passed_f, total_f, pct_f in firm_stats:
        firm_rows.append(
            f"<tr><td>{firm}</td><td>{passed_f}</td><td>{total_f}</td>"
            f"<td><strong>{pct_f}%</strong></td></tr>"
        )
    firm_section = ""
    if firm_stats:
        firm_section = f"""
<h2 class="section-title">Pass rate by firm</h2>
<table class="firm-table">
  <thead><tr><th>Firm</th><th>Passed</th><th>Total</th><th>Rate</th></tr></thead>
  <tbody>{''.join(firm_rows)}</tbody>
</table>"""
    firm_th = "<th>Firm</th>" if has_firm else ""
    trs = []
    for row in rows:
        cls = "pass" if row["passed"] else "fail"
        status = "PASS" if row["passed"] else "FAIL"
        trs.append(
            f"""<tr class="{cls}">
  <td>{row['id']}</td>
  {f"<td>{row['firm']}</td>" if has_firm else ""}
  <td><strong>{row['title']}</strong></td>
  <td class="desc">{row['description']}</td>
  <td>H{row['expected_hand']}</td>
  <td>{row['expected_dept']}</td>
  <td>H{row['actual_hand']}</td>
  <td>{row['actual_dept']}</td>
  <td><span class="badge {cls}">{status}</span></td>
</tr>"""
        )
    spec_trs = []
    for row in specialist_rows:
        spec_trs.append(
            f"""<tr>
  <td>{row['id']}</td>
  <td><strong>{row['title']}</strong></td>
  <td>{row['actual_dept']}</td>
  <td>{row['expected_dept']}</td>
  <td class="spec-path">{row['specialist_path']}</td>
</tr>"""
        )
    specialist_section = ""
    if specialist_rows:
        specialist_section = f"""
<h2 class="section-title">Routing Specialists — SecOps-owned desk</h2>
<p class="section-sub">Misroutes caught by automated tests. In production, any assignee sends these to the SecOps specialist desk for one-hop correction.</p>
<table class="specialists-table">
  <thead>
    <tr>
      <th>ID</th><th>Title</th><th>AI routed to</th><th>Correct dept</th><th>Specialist path</th>
    </tr>
  </thead>
  <tbody>
{''.join(spec_trs)}
  </tbody>
</table>"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{ --pass: #0d7a3e; --fail: #c0392b; --bg: #f4f6f8; --card: #fff; --border: #dde3ea; --accent: {accent}; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: #1a1a2e; padding: 2rem; line-height: 1.5; }}
  .header {{ background: linear-gradient(135deg, var(--accent) 0%, #12abdb 50%, #1a1a2e 100%); color: #fff; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; }}
  .header h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}
  .header p {{ opacity: 0.9; font-size: 0.95rem; }}
  .stats {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.5rem; min-width: 120px; }}
  .stat .num {{ font-size: 1.75rem; font-weight: 700; }}
  .stat .lbl {{ font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }}
  .stat.pass .num {{ color: var(--pass); }}
  .stat.fail .num {{ color: var(--fail); }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); font-size: 0.9rem; }}
  th {{ background: var(--accent); color: #fff; padding: 0.75rem 1rem; text-align: left; font-weight: 600; white-space: nowrap; }}
  td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tr.pass td {{ background: #f0faf4; }}
  tr.fail td {{ background: #fef5f4; }}
  tr:hover td {{ filter: brightness(0.97); }}
  .desc {{ max-width: 340px; color: #444; font-size: 0.85rem; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; }}
  .badge.pass {{ background: #d4edda; color: var(--pass); }}
  .badge.fail {{ background: #f8d7da; color: var(--fail); }}
  .footer {{ margin-top: 1.5rem; font-size: 0.8rem; color: #888; }}
  .section-title {{ margin: 2rem 0 0.5rem; font-size: 1.25rem; color: #1a1a2e; }}
  .section-sub {{ margin-bottom: 1rem; color: #555; font-size: 0.9rem; max-width: 720px; }}
  .specialists-table th {{ background: #7c3aed; }}
  .firm-table th {{ background: #0369a1; }}
  .firm-table {{ margin-bottom: 1.5rem; max-width: 640px; }}
  .spec-path {{ color: #5b21b6; font-weight: 600; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
<div class="stats">
  <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
  <div class="stat pass"><div class="num">{pass_count}</div><div class="lbl">Passed</div></div>
  <div class="stat fail"><div class="num">{fail}</div><div class="lbl">Failed</div></div>
  <div class="stat pass"><div class="num">{pct}%</div><div class="lbl">Pass Rate</div></div>
</div>
{firm_section}
<table>
  <thead>
    <tr>
      <th>ID</th>{firm_th}<th>Title</th><th>Description</th>
      <th>Exp Hand</th><th>Exp Dept</th><th>Act Hand</th><th>Act Dept</th><th>Result</th>
    </tr>
  </thead>
  <tbody>
{''.join(trs)}
  </tbody>
</table>
{specialist_section}
<p class="footer">Generated by SAARTHI routing test pipeline · Gemini classifier + RAG · SecOps Routing Specialists fallback</p>
</body>
</html>"""
    outfile.write_text(html, encoding="utf-8")
    return pass_count, total


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scenarios", required=True)
    p.add_argument("--results", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", required=True)
    p.add_argument("--accent", default="#0070ad")
    args = p.parse_args()
    scenarios = json.loads(Path(args.scenarios).read_text())
    results = json.loads(Path(args.results).read_text())
    rows = build_rows(scenarios, results)
    passed, total = render_html(
        args.title, args.subtitle, rows, Path(args.output), args.accent
    )
    print(f"Wrote {args.output} ({passed}/{total})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
