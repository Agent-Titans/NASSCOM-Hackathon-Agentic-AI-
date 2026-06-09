"""Phase 2 pipeline tests — run: pytest tests/ -q"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.guardrail import GuardrailAgent
from src.agents.classifier import ClassifierAgent
from src.agents.supervisor import SupervisorAgent
from src.models.schemas import ClassificationResult, ResolutionResult


def test_guardrail_redacts_email():
    g = GuardrailAgent()
    out = g.apply_guardrails("Contact me at user@company.com for VPN issue")
    assert "[EMAIL_REDACTED]" in out.text
    assert not out.blocked


def test_security_policy_hand3():
    sup = SupervisorAgent()
    decision = sup.decide(
        ClassificationResult("Security", confidence_hint="high"),
        ResolutionResult(similarity_score=0.9, low_grounding=False),
    )
    assert decision.hand == "3"
    assert decision.policy_trigger == "security_policy"


def test_keyword_classifier_access():
    c = ClassifierAgent()
    from src.models.schemas import SanitizedText

    r = c.classify(SanitizedText("I forgot my password and cannot login to portal"))
    assert r.use_case_category in ("Access Management", "Application", "Security")


def test_requester_escalation_targets_hand3():
    from src.ui.app import _escalate
    from src.db.models import Ticket, User
    from src.db.session import get_session_factory, init_db
    from src.stores.ticket_store import TicketStore

    init_db()
    Session = get_session_factory()
    with Session() as session:
        user = User(email="esc@demo.local", role="requester")
        session.add(user)
        session.commit()
        session.refresh(user)
        ticket = Ticket(
            user_id=user.user_id,
            title="VPN",
            description_raw="test",
            hand="1",
            status="SELF_HELP",
            confidence=0.85,
        )
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        tid = ticket.ticket_id
    _escalate(tid)
    with Session() as session:
        updated = TicketStore(session).get(tid)
        assert updated is not None
        assert updated.hand == "3"
        assert updated.status == "HUMAN_REVIEW"
        assert updated.escalation_required is True


def test_resolver_password_playbook_hand1_path():
    from src.agents.resolver import ResolverAgent
    from src.agents.router import RouterAgent
    from src.agents.supervisor import SupervisorAgent
    from src.models.schemas import ClassificationResult, SanitizedText

    san = SanitizedText("I forgot my password and cannot login")
    clf = ClassificationResult("Access Management", confidence_hint="high")
    route = RouterAgent().route(clf, "medium")
    res = ResolverAgent().resolve(san, clf, route)
    assert res.low_grounding is False
    assert res.similarity_score >= 0.8
    dec = SupervisorAgent().decide(clf, res, sentiment=0.85, historical_success=0.5)
    assert dec.hand == "1"
