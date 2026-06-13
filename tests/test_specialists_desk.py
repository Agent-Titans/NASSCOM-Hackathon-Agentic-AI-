"""Tests for SecOps Routing Specialists desk."""
from __future__ import annotations

import pytest

from src.config.specialists import SPECIALISTS_QUEUE, STATUS_ROUTING_REVIEW
from src.db.models import Ticket, User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.config.settings import get_settings
from src.services.specialists_desk_service import (
    can_request_specialist,
    get_specialist_context,
    keep_specialist_ticket_in_secops,
    list_specialists_queue,
    request_specialist_review,
    reroute_from_specialists,
)
from src.stores.ticket_store import TicketStore


@pytest.fixture
def specialists_session(monkeypatch, tmp_path):
    db_file = tmp_path / "specialists.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requester = User(email="req@user", role="employee")
        sw = User(email="subbu@employee", role="assignee", department="Software")
        net = User(email="shashi@employee", role="assignee", department="Network")
        hw = User(email="sree@employee", role="assignee", department="Hardware")
        secops = User(email="narsimha@employee", role="assignee", department="SecOps")
        session.add_all([requester, sw, net, hw, secops])
        session.commit()
        yield session
    get_settings.cache_clear()
    reset_db_caches()


def _make_ticket(session, *, dept="Software", hand="2", status="ROUTED"):
    user = session.query(User).filter_by(role="employee").first()
    ticket = Ticket(
        user_id=user.user_id,
        title="Misroute test",
        description_raw="Test ticket for specialists desk",
        status=status,
        hand=hand,
        department_queue=dept,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def _agent(session, dept: str) -> User:
    return session.query(User).filter_by(role="assignee", department=dept).first()


def test_request_specialist_moves_to_secops_queue(specialists_session):
    session = specialists_session
    ticket = _make_ticket(session, dept="Software")
    agent = _agent(session, "Software")
    ok, msg = request_specialist_review(
        session,
        ticket,
        agent,
        "This is clearly a network VPN issue not application software.",
    )
    assert ok, msg
    session.refresh(ticket)
    assert ticket.department_queue == SPECIALISTS_QUEUE
    assert ticket.status == STATUS_ROUTING_REVIEW
    assert ticket.assignee_id is None


def test_secops_reroute_one_hop(specialists_session):
    session = specialists_session
    ticket = _make_ticket(session, dept="Software")
    sw_agent = _agent(session, "Software")
    request_specialist_review(
        session,
        ticket,
        sw_agent,
        "VPN split tunnel issue — belongs with Network team not Software.",
    )
    secops = _agent(session, "SecOps")
    ok, msg = reroute_from_specialists(session, ticket, secops, "Network")
    assert ok, msg
    session.refresh(ticket)
    assert ticket.department_queue == "Network"
    assert ticket.status == "ROUTED"

    ok2, _ = reroute_from_specialists(session, ticket, secops, "Hardware")
    assert not ok2


def test_specialist_context_from_audit(specialists_session):
    session = specialists_session
    ticket = _make_ticket(session, dept="Hardware", hand="3")
    agent = _agent(session, "Hardware")
    reason = "Security incident misrouted to hardware — needs SecOps review path."
    request_specialist_review(session, ticket, agent, reason)
    ctx = get_specialist_context(session, ticket.ticket_id)
    assert ctx["original_department"] == "Hardware"
    assert ctx["reason"] == reason
    assert ctx["requested_by"] == agent.email


def test_secops_keeps_routing_desk_ticket(specialists_session):
    session = specialists_session
    ticket = _make_ticket(session, dept="Software")
    sw = _agent(session, "Software")
    request_specialist_review(
        session,
        ticket,
        sw,
        "VPN error 800 — likely network security issue needing SecOps review.",
    )
    secops = _agent(session, "SecOps")
    ok, msg = keep_specialist_ticket_in_secops(session, ticket, secops)
    assert ok, msg
    session.refresh(ticket)
    assert ticket.department_queue == "SecOps"
    assert ticket.assignee_id == secops.user_id
    assert ticket.department_queue != SPECIALISTS_QUEUE
    assert len(list_specialists_queue(session)) == 0


def test_secops_stats_separate_operational_and_specialists(specialists_session):
    """Routing Specialists tickets must not appear in SecOps department inbox."""
    session = specialists_session
    store = TicketStore(session)
    secops = _agent(session, "SecOps")

    # Normal SecOps H3 ticket
    h3 = _make_ticket(session, dept="SecOps", hand="3", status="HUMAN_REVIEW")
    # Misroute sent to specialists desk
    misroute = _make_ticket(session, dept="Software")
    sw = _agent(session, "Software")
    request_specialist_review(
        session,
        misroute,
        sw,
        "VPN timeout error 800 — network issue not software application.",
    )

    stats = store.department_stats("SecOps", secops.user_id)
    inbox_ids = {t.ticket_id for t in stats["tickets"]}
    assert h3.ticket_id in inbox_ids
    assert misroute.ticket_id not in inbox_ids
    assert stats["specialists_count"] == 1
    assert stats["total"] == 1

    specialists = list_specialists_queue(session)
    assert len(specialists) == 1
    assert specialists[0].ticket_id == misroute.ticket_id


def test_can_request_specialist_rules(specialists_session):
    session = specialists_session
    ticket = _make_ticket(session, dept="Network")
    net_agent = _agent(session, "Network")
    sw_agent = _agent(session, "Software")
    assert can_request_specialist(ticket, net_agent)
    assert not can_request_specialist(ticket, sw_agent)
