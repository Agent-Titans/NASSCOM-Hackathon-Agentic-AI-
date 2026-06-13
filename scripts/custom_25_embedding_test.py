#!/usr/bin/env python3
"""
Run 25 custom IT scenarios against the full ticket pipeline.

Usage:
  python scripts/custom_25_embedding_test.py --compare
  RAG_EMBEDDING_BACKEND=local python scripts/custom_25_embedding_test.py --output docs/custom_25_local.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCENARIOS_PATH = ROOT / "data" / "custom_25_scenarios.json"


def _load_cases(scenarios_path: Optional[Path] = None) -> list:
    from scripts.master_judge_test import CaseSpec

    path = scenarios_path or SCENARIOS_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list = []
    for row in data["cases"]:
        exp = row.get("expect", {})
        out.append(
            CaseSpec(
                case_id=row["id"],
                title=row["title"],
                description=row["description"],
                expected_hand=str(exp.get("hand", "2")),
                expected_department=str(exp.get("department", "Software")),
                expected_category=str(exp.get("category")) if exp.get("category") else None,
                urgency=row.get("urgency", "medium"),
                acceptable_hands=tuple(row["acceptable_hands"])
                if row.get("acceptable_hands")
                else None,
                notes=row.get("notes", path.stem),
            )
        )
    return out


def _reindex_chroma(backend: str) -> int:
    """Re-index Chroma for the given backend (no SQLite writes)."""
    os.environ["RAG_EMBEDDING_BACKEND"] = backend
    from src.config.settings import get_settings

    get_settings.cache_clear()

    from scripts.ingest_synthetic_corpus import build_chroma_entries, _load_tickets
    from src.services.ticket_retrieval import TicketRetrievalService
    from src.stores.chroma_store import ChromaTicketStore

    settings = get_settings()
    tickets = _load_tickets(settings.synthetic_corpus_path)
    entries = build_chroma_entries(tickets)
    print(f"  Re-indexing Chroma ({backend}) — {len(entries)} + KB docs…", flush=True)
    t0 = time.perf_counter()
    svc = TicketRetrievalService()
    count = svc.index_synthetic_chroma(entries)
    chroma = ChromaTicketStore()
    print(
        f"  Chroma ready: {count} docs, mode={chroma._embedding_mode}, "
        f"{time.perf_counter() - t0:.1f}s",
        flush=True,
    )
    return count


def _run_suite(
    backend: str,
    *,
    reindex: bool,
    scenarios_path: Optional[Path] = None,
    case_delay_sec: float = 1.5,
    start_index: int = 0,
    count: Optional[int] = None,
    no_clear: bool = False,
    existing_cases: Optional[list[dict]] = None,
) -> dict[str, Any]:
    os.environ["RAG_EMBEDDING_BACKEND"] = backend
    os.environ.setdefault("RAG_CORPUS_MODE", "synthetic")

    from src.config.settings import get_settings

    get_settings.cache_clear()

    from scripts.master_judge_test import (
        CaseResult,
        _check_environment,
        _clear_live_tickets,
        _get_requester,
        _process_case,
    )
    from src.db.session import get_session_factory, init_db
    from src.services.process_cache import invalidate_retrieval_cache

    if reindex:
        _reindex_chroma(backend)
    invalidate_retrieval_cache()

    init_db()
    Session = get_session_factory()
    scenarios_path = scenarios_path or SCENARIOS_PATH
    all_cases = _load_cases(scenarios_path)
    end = len(all_cases) if count is None else min(start_index + count, len(all_cases))
    cases = all_cases[start_index:end]
    results: list[CaseResult] = []

    with Session() as session:
        cleared = 0 if no_clear or start_index > 0 else _clear_live_tickets(session)
        if cleared:
            print(f"Cleared {cleared} live ticket(s).")
        env = _check_environment(session)
        requester = _get_requester(session)

        label = scenarios_path.stem.replace("_", " ")
        print(
            f"\n=== {label} — {backend} embeddings "
            f"(cases {start_index + 1}-{end} of {len(all_cases)}) ===\n",
            flush=True,
        )
        for i, spec in enumerate(cases):
            if i > 0 and case_delay_sec > 0:
                time.sleep(case_delay_sec)  # reduce Gemini 503 bursts on free tier
            _ticket, cr = _process_case(session, requester, spec)
            mark = "PASS" if cr.passed else "FAIL"
            rag = f"{cr.rag_match_id or '—'} ({cr.rag_score})"
            print(
                f"  [{mark}] {spec.case_id} {spec.title[:40]}: "
                f"H{cr.actual_hand}/{cr.actual_department} rag={rag} {cr.latency_sec}s"
            )
            results.append(cr)

    merged_by_id: dict[str, dict] = {}
    for row in existing_cases or []:
        merged_by_id[row["case_id"]] = row
    for r in results:
        merged_by_id[r.case_id] = asdict(r)
    merged = list(merged_by_id.values())
    merged.sort(key=lambda row: row["case_id"])
    passed = sum(
        1
        for r in merged
        if r.get("hand_ok") and r.get("department_ok") and r.get("category_ok", True)
    )
    return {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "scenarios_file": str(scenarios_path),
        "environment": env,
        "summary": {
            "total": len(merged),
            "passed": passed,
            "pass_rate": round(passed / len(merged), 3) if merged else 0,
            "avg_latency_sec": round(
                sum(r["latency_sec"] for r in merged) / len(merged), 2
            )
            if merged
            else 0,
        },
        "cases": merged,
    }


def _write_comparison(
    local: dict,
    gemini: dict,
    out_md: Path,
    scenarios_path: Optional[Path] = None,
) -> None:
    local_ix = {r["case_id"]: r for r in local["cases"]}
    gem_ix = {r["case_id"]: r for r in gemini["cases"]}
    path = scenarios_path or Path(local.get("scenarios_file", SCENARIOS_PATH))
    specs = {c.case_id: c for c in _load_cases(path)}

    lines = [
        "# Custom 25 IT Scenarios — Local vs Gemini Embeddings",
        "",
        f"**Local run:** {local['started_at']} · pass {local['summary']['passed']}/{local['summary']['total']} "
        f"({local['summary']['pass_rate']*100:.0f}%) · avg {local['summary']['avg_latency_sec']}s",
        f"**Gemini run:** {gemini['started_at']} · pass {gemini['summary']['passed']}/{gemini['summary']['total']} "
        f"({gemini['summary']['pass_rate']*100:.0f}%) · avg {gemini['summary']['avg_latency_sec']}s",
        "",
    ]

    for spec in _load_cases(path):
        cid = spec.case_id
        loc, gem = local_ix[cid], gem_ix[cid]
        lp = "PASS" if loc["hand_ok"] and loc["department_ok"] else "FAIL"
        gp = "PASS" if gem["hand_ok"] and gem["department_ok"] else "FAIL"
        same = (
            "same"
            if loc["actual_hand"] == gem["actual_hand"]
            and loc["actual_department"] == gem["actual_department"]
            else "**DIFF**"
        )
        exp = f"H{spec.expected_hand}/{spec.expected_department}"

        def rag_fmt(r: dict) -> str:
            mid = r.get("rag_match_id") or "—"
            sc = r.get("rag_score")
            return f"{mid} ({sc:.2f})" if sc is not None else mid

        lines.extend(
            [
                f"### {cid} — {spec.title}",
                f"**Description:** {spec.description}",
                f"**Expected:** {exp}",
                "| | Local MiniLM | Gemini embed |",
                "|---|---|---|",
                f"| Hand / Dept | H{loc['actual_hand']}/{loc['actual_department']} | H{gem['actual_hand']}/{gem['actual_department']} |",
                f"| Category | {loc['actual_category']} | {gem['actual_category']} |",
                f"| RAG match | {rag_fmt(loc)} | {rag_fmt(gem)} |",
                f"| Latency | {loc['latency_sec']:.2f}s | {gem['latency_sec']:.2f}s |",
                f"| Test result | {lp} | {gp} |",
                f"| Cross-backend routing | {same} |",
                "",
            ]
        )

    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Custom 25 embedding comparison test")
    parser.add_argument("--backend", choices=("local", "gemini"), help="Single backend run")
    parser.add_argument("--output", type=Path, help="JSON output path")
    parser.add_argument("--compare", action="store_true", help="Run both backends + write comparison")
    parser.add_argument("--no-reindex", action="store_true", help="Skip Chroma re-index")
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=SCENARIOS_PATH,
        help="Path to scenarios JSON (default: custom_25_scenarios.json)",
    )
    parser.add_argument(
        "--case-delay",
        type=float,
        default=2.0,
        help="Seconds between tickets (reduces API 503 bursts)",
    )
    parser.add_argument("--start", type=int, default=0, help="Case index to start from")
    parser.add_argument("--count", type=int, default=None, help="Number of cases to run")
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear live tickets (use with --start for resume)",
    )
    args = parser.parse_args()

    if args.compare:
        py = sys.executable
        local_out = ROOT / "docs" / "custom_25_local.json"
        gemini_out = ROOT / "docs" / "custom_25_gemini.json"
        for backend, out in (("local", local_out), ("gemini", gemini_out)):
            cmd = [py, str(__file__), "--backend", backend, "--output", str(out)]
            if args.no_reindex:
                cmd.append("--no-reindex")
            print(f"\n>>> subprocess {backend}\n")
            subprocess.run(cmd, cwd=ROOT, check=True)
        local = json.loads(local_out.read_text())
        gemini = json.loads(gemini_out.read_text())
        md = ROOT / "docs" / "CUSTOM_25_LOCAL_VS_GEMINI.md"
        _write_comparison(local, gemini, md)
        print(f"\nWrote {md}")
        print(f"Wrote {local_out}")
        print(f"Wrote {gemini_out}")
        return 0

    if not args.backend:
        parser.error("Specify --backend or --compare")
    out = args.output or ROOT / f"docs/custom_25_{args.backend}.json"
    existing: list[dict] = []
    if args.start > 0 and out.exists():
        existing = json.loads(out.read_text()).get("cases", [])

    payload = _run_suite(
        args.backend,
        reindex=not args.no_reindex,
        scenarios_path=args.scenarios,
        case_delay_sec=args.case_delay,
        start_index=args.start,
        count=args.count,
        no_clear=args.no_clear,
        existing_cases=existing if args.start > 0 else None,
    )
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {out} — {payload['summary']['passed']}/{payload['summary']['total']} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
