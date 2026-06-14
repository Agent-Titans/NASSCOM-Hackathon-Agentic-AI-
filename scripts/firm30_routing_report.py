#!/usr/bin/env python3
"""Route firm30_tickets.csv through SAARTHI pipeline and emit a routing report."""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.brand import HAND_DISPLAY  # noqa: E402
from src.db.models import ClassificationArtifact, Ticket, User  # noqa: E402
from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.rag_gate import evaluate_rag_match  # noqa: E402
from src.services.ticket_retrieval import TicketRetrievalService  # noqa: E402
from src.services.ticket_service import TicketService  # noqa: E402
from src.stores.ticket_store import TicketStore  # noqa: E402

HAND_LABEL = {k: v[0] for k, v in HAND_DISPLAY.items()}

# Golden labels: expected category (classifier) and department (router queue).
EXPECTED: dict[str, dict[str, str]] = {
    "TF01": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF02": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF03": {"category": "Network", "department": "Network", "hand": "1"},
    "TF04": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF05": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF06": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF07": {"category": "Application", "department": "Software", "hand": "2"},
    "TF08": {"category": "Infrastructure", "department": "Hardware", "hand": "2"},
    "TF09": {"category": "Database", "department": "DBA", "hand": "2"},
    "TF10": {"category": "Application", "department": "Software", "hand": "2"},
    "TF11": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF12": {"category": "Application", "department": "Software", "hand": "2"},
    "TF13": {"category": "Network", "department": "Network", "hand": "1"},
    "TF14": {"category": "Infrastructure", "department": "Hardware", "hand": "2"},
    "TF15": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF16": {"category": "Application", "department": "Software", "hand": "2"},
    "TF17": {"category": "Infrastructure", "department": "Hardware", "hand": "1"},
    "TF18": {"category": "Application", "department": "Software", "hand": "1"},
    "TF19": {"category": "Database", "department": "DBA", "hand": "2"},
    "TF20": {"category": "Network", "department": "Network", "hand": "2"},
    "TF21": {"category": "Access Management", "department": "Access Management", "hand": "1"},
    "TF22": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF23": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF24": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF25": {"category": "Database", "department": "DBA", "hand": "2"},
    "TF26": {"category": "Access Management", "department": "Access Management", "hand": "2"},
    "TF27": {"category": "Security", "department": "SecOps", "hand": "3"},
    "TF28": {"category": "Security", "department": "SecOps", "hand": "3"},
    "TF29": {"category": "Security", "department": "SecOps", "hand": "3"},
    "TF30": {"category": "Security", "department": "SecOps", "hand": "3"},
}


@dataclass
class RowResult:
    ticket_id: str
    title: str
    description: str
    expected_department: str
    expected_category: str
    expected_hand: str
    actual_hand: str
    actual_hand_label: str
    actual_department: str
    actual_category: str
    confidence: float
    classifier_source: str
    classifier_confidence_hint: str
    policy_trigger: str
    routing_reason: str
    rag_score: Optional[float]
    rag_match_id: Optional[str]
    department_correct: bool
    category_correct: bool
    hand_correct: bool
    latency_sec: float


def _hand_label(hand: str) -> str:
    return HAND_LABEL.get(hand, hand or "?")


def _routing_reason(
    *,
    policy_trigger: str,
    classifier_source: str,
    category: str,
    rag_reason: str,
    rag_score: Optional[float],
) -> str:
    parts = [
        f"Classifier: {category} ({classifier_source})",
        f"Supervisor policy: {policy_trigger}",
    ]
    if rag_score is not None:
        parts.append(f"RAG similarity {rag_score:.2f} ({rag_reason})")
    else:
        parts.append(f"RAG: {rag_reason}")
    return "; ".join(parts)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            tid = (row.get("ticket_id") or row.get("ticket_number") or "").strip()
            title = (row.get("title") or "").strip()
            description = (row.get("description") or "").strip()
            if tid and title:
                rows.append({"ticket_id": tid, "title": title, "description": description})
        return rows


def _get_requester(session) -> User:
    user = session.query(User).filter(User.email == "pallavi@user").first()
    if not user:
        user = session.query(User).filter(User.role == "requester").first()
    if not user:
        raise RuntimeError("No requester user found — run scripts/seed_users.py")
    return user


def _process_row(session, requester: User, row: dict[str, str]) -> RowResult:
    spec = EXPECTED.get(row["ticket_id"], {})
    store = TicketStore(session)
    svc = TicketService(session)
    ticket = store.create(requester, row["title"], row["description"], "medium")

    t0 = time.perf_counter()
    with patch.object(svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"):
        result = svc.process_ticket(ticket)
    elapsed = time.perf_counter() - t0
    session.refresh(ticket)

    clf = (
        session.query(ClassificationArtifact)
        .filter_by(ticket_id=ticket.ticket_id)
        .first()
    )
    retrieval_text = f"{ticket.title}\n{ticket.description_sanitized or ticket.description_raw}"
    raw = TicketRetrievalService().find_similar(session, retrieval_text)
    gate = evaluate_rag_match(raw, query_text=retrieval_text)

    category = clf.use_case_category if clf else "?"
    clf_source = result.classification.source if result.classification else "?"
    clf_hint = result.classification.confidence_hint if result.classification else "?"
    policy = (result.decision.policy_trigger or "c_total_band") if result.decision else "?"
    rag_score = round(gate.raw.similarity_score, 3) if gate.raw else None
    rag_id = gate.raw.ticket_id if gate.raw else None

    expected_dept = spec.get("department", "?")
    expected_cat = spec.get("category", "?")
    expected_hand = spec.get("hand", "?")
    actual_hand = ticket.hand or "?"
    actual_dept = ticket.department_queue or "?"

    return RowResult(
        ticket_id=row["ticket_id"],
        title=row["title"],
        description=row["description"],
        expected_department=expected_dept,
        expected_category=expected_cat,
        expected_hand=expected_hand,
        actual_hand=actual_hand,
        actual_hand_label=_hand_label(actual_hand),
        actual_department=actual_dept,
        actual_category=category,
        confidence=round(ticket.confidence or 0.0, 3),
        classifier_source=clf_source,
        classifier_confidence_hint=clf_hint,
        policy_trigger=policy,
        routing_reason=_routing_reason(
            policy_trigger=policy,
            classifier_source=clf_source,
            category=category,
            rag_reason=gate.reason,
            rag_score=rag_score,
        ),
        rag_score=rag_score,
        rag_match_id=rag_id,
        department_correct=actual_dept == expected_dept,
        category_correct=category == expected_cat,
        hand_correct=actual_hand == expected_hand,
        latency_sec=round(elapsed, 2),
    )


def _render_markdown(results: list[RowResult], summary: dict) -> str:
    lines = [
        "# Firm 30 — SAARTHI Routing Report",
        "",
        f"- **Tickets routed:** {summary['total']}",
        f"- **Department accuracy:** {summary['department_correct']}/{summary['total']} "
        f"({summary['department_accuracy_pct']:.1f}%)",
        f"- **Category accuracy:** {summary['category_correct']}/{summary['total']} "
        f"({summary['category_accuracy_pct']:.1f}%)",
        f"- **Hand accuracy:** {summary['hand_correct']}/{summary['total']} "
        f"({summary['hand_accuracy_pct']:.1f}%)",
        "",
        "## Hand distribution",
        "",
    ]
    for hand, count in summary["hand_distribution"].items():
        lines.append(f"- **{HAND_LABEL.get(hand, hand)} (Hand {hand}):** {count}")
    lines.extend(["", "## Per-ticket results", ""])
    for r in results:
        ok = "✓" if r.department_correct else "✗"
        lines.extend(
            [
                f"### {r.ticket_id} {ok}",
                f"- **Title:** {r.title}",
                f"- **Description:** {r.description}",
                f"- **Expected team:** {r.expected_department} | **Actual team:** {r.actual_department}",
                f"- **Expected category:** {r.expected_category} | **Actual category:** {r.actual_category}",
                f"- **Hand:** {r.actual_hand_label} (Hand {r.actual_hand}) — expected Hand {r.expected_hand}",
                f"- **Confidence (C_total):** {r.confidence:.3f}",
                f"- **Classifier:** {r.classifier_source} ({r.classifier_confidence_hint})",
                f"- **Reason:** {r.routing_reason}",
                "",
            ]
        )
    if summary["mismatches"]:
        lines.extend(["## Department mismatches", ""])
        for m in summary["mismatches"]:
            lines.append(
                f"- **{m['ticket_id']}** — expected **{m['expected']}**, got **{m['actual']}** "
                f"({m['category']}, Hand {m['hand']}, conf {m['confidence']:.3f})"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Route firm30 CSV tickets and report.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(r"C:\Users\Manaswini Vadrevu\Downloads\firm30_tickets.csv"),
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "docs" / "firm30_routing_report.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=ROOT / "docs" / "firm30_routing_report.md",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        return 1

    init_db()
    session = get_session_factory()()
    requester = _get_requester(session)
    rows = _load_csv(args.csv)

    results: list[RowResult] = []
    errors: list[str] = []
    for row in rows:
        try:
            results.append(_process_row(session, requester, row))
            print(
                f"  {row['ticket_id']}: Hand {results[-1].actual_hand} -> "
                f"{results[-1].actual_department}"
            )
        except Exception as exc:
            errors.append(f"{row['ticket_id']}: {exc}")
            print(f"  {row['ticket_id']}: ERROR {exc}", file=sys.stderr)

    total = len(results)
    dept_ok = sum(1 for r in results if r.department_correct)
    cat_ok = sum(1 for r in results if r.category_correct)
    hand_ok = sum(1 for r in results if r.hand_correct)
    hand_dist: dict[str, int] = {}
    for r in results:
        hand_dist[r.actual_hand] = hand_dist.get(r.actual_hand, 0) + 1

    mismatches = [
        {
            "ticket_id": r.ticket_id,
            "title": r.title,
            "expected": r.expected_department,
            "actual": r.actual_department,
            "category": r.actual_category,
            "hand": r.actual_hand,
            "confidence": r.confidence,
            "reason": r.routing_reason,
        }
        for r in results
        if not r.department_correct
    ]

    summary = {
        "total": total,
        "department_correct": dept_ok,
        "department_accuracy_pct": (dept_ok / total * 100) if total else 0.0,
        "category_correct": cat_ok,
        "category_accuracy_pct": (cat_ok / total * 100) if total else 0.0,
        "hand_correct": hand_ok,
        "hand_accuracy_pct": (hand_ok / total * 100) if total else 0.0,
        "hand_distribution": hand_dist,
        "mismatches": mismatches,
        "errors": errors,
    }

    payload = {"summary": summary, "results": [asdict(r) for r in results]}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.md_out.write_text(_render_markdown(results, summary), encoding="utf-8")

    print(
        f"\nDone — department {dept_ok}/{total} "
        f"({summary['department_accuracy_pct']:.1f}%)"
    )
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
