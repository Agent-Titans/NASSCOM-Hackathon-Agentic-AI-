#!/usr/bin/env python3
"""Compare H1 routing on two app copies — same ticket text, each local DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

_SCRIPT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else _SCRIPT_ROOT
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.agents.classifier import ClassifierAgent
from src.agents.resolver import ResolverAgent
from src.agents.router import RouterAgent
from src.agents.supervisor import SupervisorAgent
from src.db.session import get_session_factory, init_db
from src.models.schemas import SanitizedText
from src.services.historical_success_service import historical_success_for_category
from src.services.rag_gate import evaluate_rag_match
from src.services.ticket_retrieval import TicketRetrievalService

# Full H1 corpus descriptions + a few short user-style phrases
CASES = [
    ("ent-h1-01 Chrome", "Google Chrome spins forever on any website. Other apps have internet. Started after a Windows update this morning."),
    ("ent-h1-02 Password", "I forgot my company portal password and cannot sign in on my laptop. I have internet access on my phone."),
    ("ent-h1-03 WiFi", "Laptop shows connected to office Wi-Fi but browsers say no internet. Colleagues nearby are fine."),
    ("ent-h1-09 Printer", "Office printer on floor 2 says Offline in Windows. I printed successfully yesterday. I only need to print one document today."),
    ("ent-h1-13 VPN", "I'm getting an Error 807 when I try to start my VPN client. Wi-Fi works but VPN will not connect."),
    ("ent-h1-15 Keyboard", "Keyboard types symbols instead of letters after I bumped a key combo. I need to fix input language myself."),
    ("short password", "I forgot password need to reset"),
    ("short keyboard caps", "Keyboard typing in all capital letters even though Caps Lock light is off"),
    ("rag-h1-01 title only", "Forgot portal password"),
]


def run_case(session, text: str) -> dict:
    svc = TicketRetrievalService()
    # Skip slow Gemini embedding calls — Chroma + stemmed overlap still run.
    with patch(
        "src.services.semantic_similarity.GeminiClient.embed_text",
        return_value=None,
    ):
        raw = svc.find_similar(session, text)
    gate = evaluate_rag_match(raw)
    trusted = gate.trusted
    san = SanitizedText(text)
    agent = ClassifierAgent()
    with patch.object(agent.gemini, "classify_ticket", return_value=None):
        clf = agent.classify(san, similar=trusted)
    route = RouterAgent().route(clf, "medium")
    res = ResolverAgent().resolve(san, clf, route, similar=trusted)
    hist = historical_success_for_category(session, clf.use_case_category)
    if not res.low_grounding and hist <= 0.5:
        hist = 0.65
    sup = SupervisorAgent()
    dec = sup.decide(
        clf,
        res,
        sentiment=sup.sentiment_from_classification(clf),
        historical_success=hist,
    )
    return {
        "rag_id": raw.ticket_id if raw else None,
        "rag_score": round(raw.similarity_score, 3) if raw else None,
        "rag_hand": raw.source_hand if raw else None,
        "gate": gate.reason,
        "sim": round(res.similarity_score, 3),
        "src_hand": res.matched_source_hand,
        "hist": round(hist, 3),
        "c_total": round(dec.c_total, 3),
        "hand": dec.hand,
        "policy": dec.policy_trigger,
        "queue": route.department_queue,
    }


def main() -> int:
    label = sys.argv[2] if len(sys.argv) > 2 else "workspace"
    # Re-init DB against this app's data dir
    init_db()
    Session = get_session_factory()
    results = []
    with Session() as session:
        fb = session.execute(
            __import__("sqlalchemy").text(
                "SELECT COUNT(*) FROM feedback"
            )
        ).scalar()
        for name, text in CASES:
            row = run_case(session, text)
            row["name"] = name
            results.append(row)
    out = {"label": label, "app_root": str(APP_ROOT), "feedback_rows": fb, "cases": results}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
