"""Hand 1 'Did not work' → Hand 2 with department preserved + auto-assign."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.config.settings import get_settings
from src.db.models import AuditLog, Ticket, User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.services.auto_assign_service import (
    assign_escalated_ticket,
    reset_auto_assign_throttle,
    run_auto_assignments,
)
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore


@pytest.fixture
def db_session(monkeypatch, tmp_path):
    db_file = tmp_path / "h1_escalation.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requester = User(email="req@user", role="requester")
        agent = User(email="agent-hw@employee", role="assignee", department="Hardware")
        session.add_all([requester, agent])
        session.commit()
        for u in (requester, agent):
            session.refresh(u)
        yield session, requester, agent
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()


def _escalate_h1_to_h2(session, ticket_id: str) -> Ticket | None:
    """Mirror employee_portal._escalate_ticket."""
    ticket = TicketStore(session).get(ticket_id)
    if not ticket:
        return None
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
        ticket,
        "feedback_escalation",
        details="outcome=failed hand=1_to_2",
    )
    session.commit()
    if not assign_escalated_ticket(session, ticket):
        run_auto_assignments(session, force=True)
    session.refresh(ticket)
    return ticket


def test_h1_not_worked_routes_to_department_and_auto_assigns(db_session):
    session, requester, agent = db_session
    old = datetime.utcnow() - timedelta(minutes=15)
    ticket = Ticket(
        user_id=requester.user_id,
        title="Laptop fan noise",
        description_raw="Fan loud after update",
        hand="1",
        status="SELF_HELP",
        department_queue="Hardware",
        priority="P2",
        sla_hours=24,
        confidence=0.82,
        created_at=old,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    result = _escalate_h1_to_h2(session, ticket.ticket_id)

    assert result is not None
    assert result.hand == "2"
    assert result.department_queue == "Hardware"

    audit = (
        session.query(AuditLog)
        .filter_by(ticket_id=ticket.ticket_id, event_type="feedback_escalation")
        .first()
    )
    assert audit is not None
    assert "1_to_2" in (audit.details or "")
    assert result.assignee_id == agent.user_id
    assert result.status == "IN_PROGRESS"
