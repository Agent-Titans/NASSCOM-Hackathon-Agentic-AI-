#!/usr/bin/env python3
"""Pre-demo smoke check — golden ticket routing expectations (strict LLD)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.classifier import ClassifierAgent
from src.agents.resolver import ResolverAgent
from src.agents.router import RouterAgent
from src.agents.supervisor import SupervisorAgent
from src.config.supervisor_policy import get_supervisor_policy
from src.db.session import get_session_factory, init_db
from src.models.schemas import SanitizedText
from src.services.rag_gate import evaluate_rag_match
from src.services.ticket_retrieval import TicketRetrievalService

_CASES = [
    {
        "name": "AWS secret leak",
        "text": (
            "Urgent security cleanup needed for public repository. "
            "I accidentally pushed my raw AWS secret access key to a public GitHub branch."
        ),
        "expect_category": "Security",
        "expect_hand": "3",
        "expect_queue": "SecOps",
    },
    {
        "name": "Windows password reset",
        "text": (
            "How do I reset my Windows login password? "
            "I am locked out of my active directory account and need the link to reset "
            "my corporate password"
        ),
        "expect_category": "Access Management",
        "expect_hand": "2",
        "expect_queue": "Identity",
    },
    {
        "name": "Chrome cache H1 enterprise",
        "text": (
            "Google Chrome spins forever on any website. Other apps have internet. "
            "Started after a Windows update this morning."
        ),
        "expect_category": "Application",
        "expect_hand": "1",
        "expect_queue": "Software",
    },
    {
        "name": "VPN error 807 midnight",
        "text": "I'm getting an Error 807 when I try to start my VPN client.",
        "expect_category": "Network",
        "expect_hand_not": "3",
        "expect_queue": "Network",
    },
    {
        "name": "IP whitelist SQL",
        "text": "I need someone to whitelist my IP so I can reach the SQL database.",
        "expect_category": "Network",
        "expect_hand_not": "3",
        "expect_queue": "Network",
    },
    {
        "name": "Docker hypervisor",
        "text": (
            "Docker Desktop failing to start / Hypervisor error. "
            "Hardware-assisted virtualization must be enabled in the BIOS. "
            "It worked fine yesterday before the system security policy updates ran overnight."
        ),
        "expect_category_not": "Security",
        "expect_hand_not": "3",
    },
]


def _run_case(case: dict) -> tuple[bool, str]:
    san = SanitizedText(case["text"])
    init_db()
    Session = get_session_factory()
    with Session() as session:
        raw = TicketRetrievalService().find_similar(session, case["text"])
    trusted = evaluate_rag_match(raw).trusted

    agent = ClassifierAgent()
    with patch.object(agent.gemini, "classify_ticket", return_value=None):
        clf = agent.classify(san, similar=trusted)

    if case.get("expect_category") and clf.use_case_category != case["expect_category"]:
        return False, f"category={clf.use_case_category}"
    if case.get("expect_category_not") == "Security" and clf.use_case_category == "Security":
        return False, "false Security classification"

    route = RouterAgent().route(clf, "medium")
    if case.get("expect_queue") and route.department_queue != case["expect_queue"]:
        return False, f"queue={route.department_queue}"

    res = ResolverAgent().resolve(san, clf, route, similar=trusted)
    hist = 0.65 if trusted and not res.low_grounding else 0.5
    dec = SupervisorAgent().decide(
        clf,
        res,
        sentiment=SupervisorAgent().sentiment_from_classification(clf),
        historical_success=hist,
    )
    if case.get("expect_hand") and dec.hand != case["expect_hand"]:
        return False, f"hand={dec.hand} trigger={dec.policy_trigger}"
    if case.get("expect_hand_not") == "3" and dec.hand == "3":
        return False, f"hand=3 trigger={dec.policy_trigger}"
    return True, f"hand={dec.hand} queue={route.department_queue}"


def main() -> int:
    policy = get_supervisor_policy()
    print(f"Supervisor mode: {policy.mode}")
    failed = 0
    for case in _CASES:
        ok, detail = _run_case(case)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {case['name']}: {detail}")
        if not ok:
            failed += 1
    if failed:
        print(f"\n{failed} case(s) failed.")
        return 1
    print("\nAll golden smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
