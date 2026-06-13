"""Integration: Hand 1/2/3 routing, department queues, and auto-assign."""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.config.settings import get_settings
from src.db.models import AuditLog, Ticket, User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.services.auto_assign_service import (
    _agents_for_department,
    assign_escalated_ticket,
    reset_auto_assign_throttle,
    run_auto_assignments,
)
from src.services.ticket_service import TicketService
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore


@pytest.fixture
def routing_db(monkeypatch, tmp_path):
    db_file = tmp_path / "hand_routing.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requester = User(email="req@routing", role="requester")
        sw_agent = User(email="sw@employee", role="assignee", department="Software")
        hw_agent = User(email="hw@employee", role="assignee", department="Hardware")
        sec_agent = User(email="sec@employee", role="assignee", department="SecOps")
        access_agent = User(
            email="access@employee", role="assignee", department="Access Management"
        )
        net_agent = User(email="net@employee", role="assignee", department="Network")
        session.add_all([requester, sw_agent, hw_agent, sec_agent, access_agent, net_agent])
        session.commit()
        for u in (requester, sw_agent, hw_agent, sec_agent, access_agent, net_agent):
            session.refresh(u)
        yield session, requester, sw_agent, hw_agent, sec_agent, access_agent, net_agent
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()


def _process(session, requester: User, title: str, description: str, urgency: str = "medium"):
    ticket = TicketStore(session).create(requester, title, description, urgency)
    svc = TicketService(session)
    with patch.object(svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"):
        result = svc.process_ticket(ticket)
    session.refresh(ticket)
    return ticket, result


def _age_ticket(session, ticket: Ticket, *, minutes: int) -> None:
    ticket.created_at = datetime.utcnow() - timedelta(minutes=minutes)
    session.commit()
    session.refresh(ticket)


def _escalate_h1(session, ticket_id: str) -> Ticket:
    ticket = TicketStore(session).get(ticket_id)
    assert ticket is not None
    TicketStore(session).update_hand(
        ticket,
        hand="2",
        confidence=ticket.confidence or 0.5,
        status="ROUTED",
        department_queue=ticket.department_queue,
        priority=ticket.priority,
        sla_hours=ticket.sla_hours,
        escalation_required=False,
    )
    AuditLogStore(session).record(
        ticket, "feedback_escalation", details="outcome=failed hand=1_to_2"
    )
    session.commit()
    if not assign_escalated_ticket(session, ticket):
        run_auto_assignments(session, force=True)
    session.refresh(ticket)
    return ticket


def test_hand1_password_self_help_no_assignee(routing_db):
    session, requester, _, _, _, _, _ = routing_db
    ticket, result = _process(
        session,
        requester,
        "Forgot password",
        "I forgot my password and cannot login to the company portal",
    )
    assert result.decision is not None
    assert ticket.hand == "1"
    assert ticket.status == "SELF_HELP"
    assert ticket.department_queue == "Access Management"
    assert ticket.assignee_id is None
    assert run_auto_assignments(session, force=True) == 0


def test_hand2_routes_to_department_and_auto_assigns(routing_db):
    session, requester, sw_agent, _, _, _, _ = routing_db
    ticket, result = _process(
        session,
        requester,
        "Cognos DB config",
        "[Other] Need help to configure DB2 details for IBM Cognos framework manager",
    )
    assert result.decision is not None
    assert ticket.hand == "2"
    assert ticket.status == "ROUTED"
    assert ticket.department_queue is not None
    dept_agents = _agents_for_department(session, ticket.department_queue)
    assert dept_agents, f"no agents seeded for {ticket.department_queue}"
    assert ticket.assignee_id is None

    _age_ticket(session, ticket, minutes=15)
    assert run_auto_assignments(session, force=True) == 1
    session.refresh(ticket)
    assert ticket.assignee_id is not None
    assert ticket.status == "IN_PROGRESS"
    allowed = {a.user_id for a in dept_agents}
    assert ticket.assignee_id in allowed


def test_hand3_security_routes_secops_and_auto_assigns(routing_db):
    session, requester, sw_agent, hw_agent, sec_agent, access_agent, net_agent = routing_db
    ticket, result = _process(
        session,
        requester,
        "VPN breach",
        "Possible security breach on VPN - unauthorized access detected on admin account",
        urgency="high",
    )
    assert result.decision is not None
    assert ticket.hand == "3"
    assert ticket.department_queue == "SecOps"
    assert ticket.escalation_required is True
    assert ticket.assignee_id is None

    _age_ticket(session, ticket, minutes=15)
    assert run_auto_assignments(session, force=True) == 1
    session.refresh(ticket)
    assert ticket.assignee_id is not None
    assert ticket.status == "IN_PROGRESS"
    # Hand 3 triage may assign any available assignee on the roster.
    all_agents = {
        sw_agent.user_id,
        hw_agent.user_id,
        sec_agent.user_id,
        access_agent.user_id,
        net_agent.user_id,
    }
    assert ticket.assignee_id in all_agents


def test_hand1_not_worked_escalates_then_assigns_in_department(routing_db):
    session, requester, _, _, _, access_agent, _ = routing_db
    ticket, _ = _process(
        session,
        requester,
        "Forgot password",
        "I forgot my password and cannot login to the company portal",
    )
    assert ticket.hand == "1"
    assert ticket.department_queue == "Access Management"

    escalated = _escalate_h1(session, ticket.ticket_id)
    assert escalated.hand == "2"
    assert escalated.department_queue == "Access Management"
    assert escalated.assignee_id == access_agent.user_id
    assert escalated.status == "IN_PROGRESS"
