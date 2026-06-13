"""Agent workspace — department queue isolation and inbox filters."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.config.settings import get_settings
from src.db.models import Ticket, User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.services.auto_assign_service import reset_auto_assign_throttle
from src.stores.ticket_store import TicketStore
from src.ui.agent_portal import _filter_tickets


@pytest.fixture
def agent_filter_db(monkeypatch, tmp_path):
    db_file = tmp_path / "agent_filters.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        agents = {
            "Software": User(email="sw@employee", role="assignee", department="Software"),
            "Hardware": User(email="hw@employee", role="assignee", department="Hardware"),
            "SecOps": User(email="sec@employee", role="assignee", department="SecOps"),
            "Network": User(email="net@employee", role="assignee", department="Network"),
            "DBA": User(email="dba@employee", role="assignee", department="DBA"),
            "Access Management": User(
                email="access@employee", role="assignee", department="Access Management"
            ),
        }
        requester = User(email="req@filters", role="requester")
        session.add_all([requester, *agents.values()])
        session.commit()
        for u in [requester, *agents.values()]:
            session.refresh(u)
        yield session, requester, agents
    get_settings.cache_clear()
    reset_db_caches()
    reset_auto_assign_throttle()


def _add_h2_ticket(
    session,
    requester: User,
    *,
    title: str,
    department: str,
    assignee: User | None = None,
    sla_hours: int = 24,
    created_minutes_ago: int = 0,
) -> Ticket:
    ticket = Ticket(
        user_id=requester.user_id,
        title=title,
        description_raw=title,
        hand="2",
        status="IN_PROGRESS" if assignee else "ROUTED",
        department_queue=department,
        priority="P2",
        sla_hours=sla_hours,
        assignee_id=assignee.user_id if assignee else None,
        created_at=datetime.utcnow() - timedelta(minutes=created_minutes_ago),
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@pytest.mark.parametrize(
    "dept",
    ["Software", "Hardware", "SecOps", "Network", "DBA", "Access Management"],
)
def test_list_for_department_only_shows_own_queue(agent_filter_db, dept):
    session, requester, agents = agent_filter_db
    store = TicketStore(session)
    all_depts = list(agents.keys())
    tickets_by_dept = {}
    for d in all_depts:
        tickets_by_dept[d] = _add_h2_ticket(
            session,
            requester,
            title=f"{d} issue",
            department=d,
            assignee=agents[d] if d == dept else None,
        )

    visible = store.list_for_department(dept)
    visible_ids = {t.ticket_id for t in visible}
    assert tickets_by_dept[dept].ticket_id in visible_ids
    for other in all_depts:
        if other == dept:
            continue
        assert tickets_by_dept[other].ticket_id not in visible_ids


def test_department_stats_counts(agent_filter_db):
    session, requester, agents = agent_filter_db
    store = TicketStore(session)
    me = agents["Software"]
    _add_h2_ticket(session, requester, title="Unassigned SW", department="Software")
    _add_h2_ticket(
        session,
        requester,
        title="Mine SW",
        department="Software",
        assignee=me,
    )
    _add_h2_ticket(session, requester, title="HW only", department="Hardware")

    stats = store.department_stats("Software", me.user_id)
    assert stats["total"] == 2
    assert stats["mine"] == 1
    assert stats["unassigned"] == 1


def test_inbox_filter_all(agent_filter_db):
    session, requester, agents = agent_filter_db
    me = agents["Network"]
    t1 = _add_h2_ticket(session, requester, title="A", department="Network")
    t2 = _add_h2_ticket(
        session, requester, title="B", department="Network", assignee=me
    )
    tickets = TicketStore(session).list_for_department("Network")
    filtered = _filter_tickets(tickets, "All", me)
    assert {x.ticket_id for x in filtered} == {t1.ticket_id, t2.ticket_id}


def test_inbox_filter_unassigned(agent_filter_db):
    session, requester, agents = agent_filter_db
    me = agents["Network"]
    t_open = _add_h2_ticket(session, requester, title="Open", department="Network")
    _add_h2_ticket(
        session, requester, title="Taken", department="Network", assignee=me
    )
    tickets = TicketStore(session).list_for_department("Network")
    filtered = _filter_tickets(tickets, "Unassigned", me)
    assert len(filtered) == 1
    assert filtered[0].ticket_id == t_open.ticket_id


def test_inbox_filter_mine(agent_filter_db):
    session, requester, agents = agent_filter_db
    me = agents["Hardware"]
    _add_h2_ticket(session, requester, title="Open", department="Hardware")
    t_mine = _add_h2_ticket(
        session, requester, title="Mine", department="Hardware", assignee=me
    )
    tickets = TicketStore(session).list_for_department("Hardware")
    filtered = _filter_tickets(tickets, "Mine", me)
    assert len(filtered) == 1
    assert filtered[0].ticket_id == t_mine.ticket_id


def test_inbox_filter_sla_at_risk(agent_filter_db):
    session, requester, agents = agent_filter_db
    me = agents["SecOps"]
    _add_h2_ticket(
        session,
        requester,
        title="OK SLA",
        department="SecOps",
        sla_hours=24,
        created_minutes_ago=60,
    )
    t_risk = _add_h2_ticket(
        session,
        requester,
        title="Risk SLA",
        department="SecOps",
        sla_hours=4,
        created_minutes_ago=240,
        assignee=me,
    )
    tickets = TicketStore(session).list_for_department("SecOps")
    filtered = _filter_tickets(tickets, "SLA at risk", me)
    assert len(filtered) == 1
    assert filtered[0].ticket_id == t_risk.ticket_id
