"""Shared golden-set evaluation for pytest and scripts."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

from src.db.models import ClassificationArtifact, User
from src.services.ticket_service import TicketService
from src.stores.ticket_store import TicketStore

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "data" / "golden_tickets.json"


@dataclass
class GoldenCaseResult:
    case_id: str
    title: str
    expected: dict[str, str]
    actual: dict[str, str]
    category_ok: bool
    hand_ok: bool
    department_ok: bool

    @property
    def passed(self) -> bool:
        return self.category_ok and self.hand_ok and self.department_ok


@dataclass
class GoldenReport:
    results: list[GoldenCaseResult] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def classification_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.category_ok) / self.total

    @property
    def hand_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.hand_ok) / self.total

    @property
    def routing_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.department_ok) / self.total

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    def meets_thresholds(self) -> bool:
        t = self.thresholds
        return (
            self.classification_accuracy >= t.get("classification_accuracy", 0.85)
            and self.hand_accuracy >= t.get("hand_accuracy", 0.85)
            and self.routing_accuracy >= t.get("routing_accuracy", 0.85)
        )

    def failures(self) -> list[GoldenCaseResult]:
        return [r for r in self.results if not r.passed]

    def summary_lines(self) -> list[str]:
        lines = [
            f"Golden set: {self.total} tickets",
            f"  Classification: {self.classification_accuracy:.1%}",
            f"  Hand routing:     {self.hand_accuracy:.1%}",
            f"  Department:       {self.routing_accuracy:.1%}",
        ]
        for r in self.failures():
            lines.append(
                f"  FAIL {r.case_id}: expected {r.expected} got {r.actual}"
            )
        return lines


def load_golden_cases(path: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, float]]:
    data = json.loads((path or GOLDEN_PATH).read_text(encoding="utf-8"))
    return data["cases"], data.get("thresholds", {})


def run_golden_set(session, *, mock_classifier: bool = True) -> GoldenReport:
    cases, thresholds = load_golden_cases()
    requester = session.query(User).filter(User.role == "requester").first()
    if requester is None:
        requester = User(email="golden@runner", role="requester")
        session.add(requester)
        session.commit()
        session.refresh(requester)

    svc = TicketService(session)
    report = GoldenReport(thresholds=thresholds)

    for case in cases:
        expect = case["expect"]
        ticket = TicketStore(session).create(
            requester,
            case["title"],
            case["description"],
            case.get("urgency", "medium"),
        )
        patches = [
            patch.object(
                svc.guardrail.gemini,
                "scan_prompt_injection",
                return_value="SECURITY_OK",
            ),
            patch.object(
                svc.resolver.gemini,
                "generate_resolution",
                return_value={
                    "steps": ["Review the recommended playbook steps."],
                    "citations": [],
                },
            ),
        ]
        if mock_classifier:
            patches.append(
                patch.object(svc.classifier.gemini, "classify_ticket", return_value=None)
            )

        from contextlib import ExitStack

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            svc.process_ticket(ticket)
        session.refresh(ticket)

        clf = (
            session.query(ClassificationArtifact)
            .filter_by(ticket_id=ticket.ticket_id)
            .first()
        )
        actual = {
            "category": clf.use_case_category if clf else "?",
            "hand": ticket.hand or "?",
            "department": ticket.department_queue or "?",
        }
        report.results.append(
            GoldenCaseResult(
                case_id=case["id"],
                title=case["title"],
                expected=expect,
                actual=actual,
                category_ok=actual["category"] == expect.get("category"),
                hand_ok=actual["hand"] == expect.get("hand"),
                department_ok=actual["department"] == expect.get("department"),
            )
        )

    return report
