"""Auto-assign idle queue tickets to least-loaded team agent."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.config.settings import get_settings
from src.db.models import AuditLog, Ticket, User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.services.auto_assign_service import (
    is_triage_ticket,
    pick_agent_for_ticket,
    pick_least_loaded_agent,
    pick_triage_agent,
    reset_auto_assign_throttle,
    run_auto_assignments,
)
from src.stores.ticket_store import TicketStore


@pytest.fixture
def db_session(monkeypatch, tmp_path):
    db_file = tmp_path / "auto_assign.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requester = User(email="req@user", role="requester")
        agent_a = User(email="agent-a@employee", role="assignee", department="Software")
        agent_b = User(email="agent-b@employee", role="assignee", department="Software")
        session.add_all([requester, agent_a, agent_b])
        session.commit()
        for u in (requester, agent_a, agent_b):
            session.refresh(u)
        yield session, requester, agent_a, agent_b
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()


def _queue_ticket(
    session,
    requester: User,
    *,
    created_at: datetime,
    hand: str = "2",
    department: str = "Software",
    assignee_id: str | None = None,
) -> Ticket:
    ticket = Ticket(
        user_id=requester.user_id,
        assignee_id=assignee_id,
        title="VPN issue",
        description_raw="Cannot connect",
        hand=hand,
        status="ROUTED",
        department_queue=department,
        created_at=created_at,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def test_auto_assign_skips_tickets_within_grace_window(db_session):
    session, requester, _, _ = db_session
    recent = datetime.utcnow() - timedelta(minutes=5)
    ticket = _queue_ticket(session, requester, created_at=recent)

    assigned = run_auto_assignments(session)

    assert assigned == 0
    refreshed = session.get(Ticket, ticket.ticket_id)
    assert refreshed is not None
    assert refreshed.assignee_id is None


def test_auto_assign_picks_least_loaded_agent(db_session):
    session, requester, agent_a, agent_b = db_session
    old = datetime.utcnow() - timedelta(minutes=15)
    _queue_ticket(session, requester, created_at=old, assignee_id=agent_a.user_id)
    ticket = _queue_ticket(session, requester, created_at=old)

    assigned = run_auto_assignments(session)

    assert assigned == 1
    refreshed = session.get(Ticket, ticket.ticket_id)
    assert refreshed is not None
    assert refreshed.assignee_id == agent_b.user_id
    assert refreshed.status == "IN_PROGRESS"


def test_auto_assign_ignores_hand1_and_already_owned(db_session):
    session, requester, agent_a, _ = db_session
    old = datetime.utcnow() - timedelta(minutes=20)
    hand1 = _queue_ticket(session, requester, created_at=old, hand="1", department="Software")
    owned = _queue_ticket(
        session,
        requester,
        created_at=old,
        assignee_id=agent_a.user_id,
    )

    assigned = run_auto_assignments(session)

    assert assigned == 0
    assert session.get(Ticket, hand1.ticket_id).assignee_id is None
    assert session.get(Ticket, owned.ticket_id).assignee_id == agent_a.user_id


def test_list_for_department_triggers_auto_assign(db_session):
    session, requester, agent_a, agent_b = db_session
    old = datetime.utcnow() - timedelta(minutes=12)
    ticket = _queue_ticket(session, requester, created_at=old)

    TicketStore(session).list_for_department("Software")

    refreshed = session.get(Ticket, ticket.ticket_id)
    assert refreshed is not None
    assert refreshed.assignee_id in {agent_a.user_id, agent_b.user_id}


def test_pick_least_loaded_agent_tie_breaks_by_email(db_session):
    session, _, agent_a, agent_b = db_session
    chosen = pick_least_loaded_agent(session, "Software")
    assert chosen is not None
    assert chosen.email == min(agent_a.email, agent_b.email)


def test_auto_assign_prefers_agent_who_worked_similar_ticket(db_session):
    session, requester, agent_a, agent_b = db_session
    old = datetime.utcnow() - timedelta(minutes=15)
    similar = Ticket(
        user_id=requester.user_id,
        assignee_id=agent_a.user_id,
        title="VPN fix",
        description_raw="resolved vpn",
        hand="2",
        status="RESOLVED",
        department_queue="Software",
        created_at=old,
    )
    session.add(similar)
    session.commit()
    session.refresh(similar)

    ticket = _queue_ticket(session, requester, created_at=old)
    session.add(
        AuditLog(
            ticket_id=ticket.ticket_id,
            event_type="rag_hit",
            agent="retrieval",
            details=f"ticket={similar.ticket_id[:8]} score=0.82 hand=2 gate=trusted",
        )
    )
    session.commit()

    assigned = run_auto_assignments(session)

    assert assigned == 1
    refreshed = session.get(Ticket, ticket.ticket_id)
    assert refreshed is not None
    assert refreshed.assignee_id == agent_a.user_id


def test_escalated_h2_waits_grace_from_escalation_not_creation(db_session):
    session, requester, agent_a, _ = db_session
    created = datetime.utcnow() - timedelta(minutes=30)
    ticket = _queue_ticket(session, requester, created_at=created, hand="1")
    ticket.status = "ROUTED"
    ticket.hand = "2"
    session.add(
        AuditLog(
            ticket_id=ticket.ticket_id,
            event_type="feedback_escalation",
            details="outcome=failed hand=1_to_2",
            timestamp=datetime.utcnow() - timedelta(minutes=3),
        )
    )
    session.commit()

    assert run_auto_assignments(session) == 0

    session.query(AuditLog).filter_by(ticket_id=ticket.ticket_id).update(
        {"timestamp": datetime.utcnow() - timedelta(minutes=12)}
    )
    session.commit()
    assert run_auto_assignments(session, force=True) == 1
    assert session.get(Ticket, ticket.ticket_id).assignee_id == agent_a.user_id


def test_pick_agent_for_ticket_falls_back_when_prior_overloaded(db_session):
    session, requester, agent_a, agent_b = db_session
    old = datetime.utcnow() - timedelta(minutes=15)
    similar = Ticket(
        user_id=requester.user_id,
        assignee_id=agent_a.user_id,
        title="VPN fix",
        description_raw="resolved vpn",
        hand="2",
        status="RESOLVED",
        department_queue="Software",
        created_at=old,
    )
    session.add(similar)
    session.commit()
    session.refresh(similar)

    _queue_ticket(session, requester, created_at=old, assignee_id=agent_a.user_id)
    _queue_ticket(session, requester, created_at=old, assignee_id=agent_a.user_id)
    new_ticket = _queue_ticket(session, requester, created_at=old)
    session.add(
        AuditLog(
            ticket_id=new_ticket.ticket_id,
            event_type="rag_hit",
            agent="retrieval",
            details=f"ticket={similar.ticket_id[:8]} score=0.80 hand=2 gate=trusted",
        )
    )
    session.commit()

    chosen = pick_agent_for_ticket(session, new_ticket)
    assert chosen is not None
    assert chosen.user_id == agent_b.user_id


def test_is_triage_ticket_hand3():
    ticket = Ticket(
        user_id="u",
        title="review",
        description_raw="x",
        hand="3",
        status="HUMAN_REVIEW",
    )
    assert is_triage_ticket(ticket)


def test_triage_auto_assign_picks_from_any_department(db_session):
    session, requester, agent_a, agent_b = db_session
    hardware = User(email="agent-hw@employee", role="assignee", department="Hardware")
    session.add(hardware)
    session.commit()
    session.refresh(hardware)

    old = datetime.utcnow() - timedelta(minutes=12)
    ticket = Ticket(
        user_id=requester.user_id,
        title="Security review",
        description_raw="needs specialist",
        hand="3",
        status="HUMAN_REVIEW",
        department_queue="SecOps",
        escalation_required=True,
        created_at=old,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    assigned = run_auto_assignments(session)
    assert assigned == 1
    refreshed = session.get(Ticket, ticket.ticket_id)
    assert refreshed is not None
    assert refreshed.assignee_id in {
        agent_a.user_id,
        agent_b.user_id,
        hardware.user_id,
    }


def test_pick_triage_agent_respects_capacity(db_session):
    session, requester, agent_a, agent_b = db_session
    old = datetime.utcnow() - timedelta(minutes=15)
    _queue_ticket(
        session,
        requester,
        created_at=old,
        hand="3",
        department="SecOps",
        assignee_id=agent_a.user_id,
    )
    _queue_ticket(
        session,
        requester,
        created_at=old,
        hand="3",
        department="SecOps",
        assignee_id=agent_a.user_id,
    )
    ticket = Ticket(
        user_id=requester.user_id,
        title="Triage",
        description_raw="x",
        hand="3",
        status="HUMAN_REVIEW",
        department_queue="SecOps",
        created_at=old,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    chosen = pick_triage_agent(session, ticket)
    assert chosen is not None
    assert chosen.user_id == agent_b.user_id
