"""Aggregate metrics for the admin helpdesk dashboard."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.config.departments import DEPARTMENT_QUEUES, canonical_department, display_department
from src.config.specialists import (
    EVENT_SPECIALIST_REQUESTED,
    SPECIALISTS_QUEUE,
    STATUS_ROUTING_REVIEW,
)
from src.config.demo_profiles import AGENT_QUEUE_LABELS
from src.db.models import AuditLog, Ticket, User

_CLOSED = frozenset({"RESOLVED", "CLOSED"})
_OPEN = frozenset(
    {
        "RECEIVED",
        "SELF_HELP",
        "ROUTED",
        "IN_PROGRESS",
        "HUMAN_REVIEW",
        "ESCALATED",
        "ROUTING_REVIEW",
    }
)


@dataclass
class TeamLoad:
    name: str
    open_count: int
    agent_count: int
    capacity_pct: int
    note: str


@dataclass
class AdminDashboardStats:
    total_tickets: int = 0
    open_count: int = 0
    with_agent: int = 0
    pending_user: int = 0
    resolved_count: int = 0
    closed_count: int = 0
    triage_count: int = 0
    in_triage_status: int = 0
    hand_counts: dict[str, int] = field(default_factory=dict)
    status_counts: dict[str, int] = field(default_factory=dict)
    confidence_high: int = 0
    confidence_medium: int = 0
    confidence_low: int = 0
    auto_resolved_pct: int = 0
    auto_resolved_count: int = 0
    avg_resolution_hours: float = 0.0
    total_week_delta_pct: Optional[int] = None
    resolution_week_delta_h: Optional[float] = None
    team_loads: list[TeamLoad] = field(default_factory=list)
    near_capacity_teams: int = 0
    recent_tickets: list[Ticket] = field(default_factory=list)
    all_tickets: list[Ticket] = field(default_factory=list)
    triage_tickets: list[Ticket] = field(default_factory=list)
    requester_emails: dict[str, str] = field(default_factory=dict)
    assignee_emails: dict[str, str] = field(default_factory=dict)
    specialists_open: int = 0
    specialists_routing_resolved: int = 0


def _resolution_hours(ticket: Ticket) -> Optional[float]:
    if not ticket.created_at or not ticket.updated_at:
        return None
    if ticket.status not in _CLOSED:
        return None
    delta = ticket.updated_at - ticket.created_at
    return max(delta.total_seconds() / 3600.0, 0.1)


def _operational_ticket_query(session):
    """Exclude RAG seed rows — dashboard tracks live user-submitted tickets only."""
    q = session.query(Ticket)
    for prefix in ("rag-", "kb-", "ent-"):
        q = q.filter(~Ticket.ticket_id.like(f"{prefix}%"))
    return q


def _week_delta(session: Session) -> tuple[Optional[int], Optional[float]]:
    now = datetime.utcnow()
    week = now - timedelta(days=7)
    prev = now - timedelta(days=14)

    this_week = (
        _operational_ticket_query(session)
        .filter(Ticket.created_at >= week)
        .count()
    )
    last_week = (
        _operational_ticket_query(session)
        .filter(Ticket.created_at >= prev, Ticket.created_at < week)
        .count()
    )
    total_delta = None
    if last_week > 0:
        total_delta = int(round((this_week - last_week) / last_week * 100))

    def _avg_hours(since: datetime, until: Optional[datetime] = None) -> Optional[float]:
        q = _operational_ticket_query(session).filter(Ticket.status.in_(tuple(_CLOSED)))
        q = q.filter(Ticket.updated_at >= since)
        if until:
            q = q.filter(Ticket.updated_at < until)
        rows = q.all()
        hrs = [_resolution_hours(t) for t in rows]
        hrs = [h for h in hrs if h is not None]
        return sum(hrs) / len(hrs) if hrs else None

    cur_avg = _avg_hours(week)
    prev_avg = _avg_hours(prev, week)
    res_delta = None
    if cur_avg is not None and prev_avg is not None:
        res_delta = round(cur_avg - prev_avg, 1)
    return total_delta, res_delta


def get_admin_dashboard_stats(session: Session) -> AdminDashboardStats:
    tickets = (
        _operational_ticket_query(session)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    users = {u.user_id: u.email for u in session.query(User).all()}
    # Use the canonical demo roster — not every legacy assignee row in SQLite.
    agents_by_dept: dict[str, int] = defaultdict(int)
    for email, dept in AGENT_QUEUE_LABELS.items():
        if email == "admin@employee":
            continue
        agents_by_dept[canonical_department(dept)] += 1

    stats = AdminDashboardStats()
    stats.all_tickets = tickets
    stats.total_tickets = len(tickets)
    stats.requester_emails = users
    stats.assignee_emails = users

    open_tickets: list[Ticket] = []
    for t in tickets:
        hand = t.hand or ""
        if hand:
            stats.hand_counts[hand] = stats.hand_counts.get(hand, 0) + 1

        conf = t.confidence or 0.0
        if hand:
            if conf >= 0.80:
                stats.confidence_high += 1
            elif conf >= 0.60:
                stats.confidence_medium += 1
            else:
                stats.confidence_low += 1

        if t.status in _CLOSED:
            if t.status == "RESOLVED":
                stats.resolved_count += 1
            else:
                stats.closed_count += 1
        else:
            open_tickets.append(t)

        status_key = _status_bucket(t.status)
        stats.status_counts[status_key] = stats.status_counts.get(status_key, 0) + 1

        if (
            t.hand == "3"
            or t.status in ("HUMAN_REVIEW", "ESCALATED", STATUS_ROUTING_REVIEW)
            or t.escalation_required
            or t.department_queue == SPECIALISTS_QUEUE
        ):
            stats.triage_tickets.append(t)

    stats.open_count = len(open_tickets)
    stats.with_agent = sum(1 for t in open_tickets if t.assignee_id)
    stats.pending_user = sum(
        1 for t in open_tickets if not t.assignee_id and t.hand != "1"
    )
    stats.triage_count = len(
        {
            t.ticket_id
            for t in open_tickets
            if t.hand == "3"
            or t.status in ("HUMAN_REVIEW", "ESCALATED", STATUS_ROUTING_REVIEW)
            or t.escalation_required
            or t.department_queue == SPECIALISTS_QUEUE
        }
    )
    stats.in_triage_status = stats.status_counts.get("Routing Specialists", 0)

    hand1 = stats.hand_counts.get("1", 0)
    routed = stats.hand_counts.get("1", 0) + stats.hand_counts.get("2", 0) + stats.hand_counts.get("3", 0)
    if routed:
        stats.auto_resolved_pct = int(round(hand1 / routed * 100))
    stats.auto_resolved_count = hand1

    hrs = [_resolution_hours(t) for t in tickets]
    hrs = [h for h in hrs if h is not None]
    if hrs:
        stats.avg_resolution_hours = round(sum(hrs) / len(hrs), 1)

    stats.total_week_delta_pct, stats.resolution_week_delta_h = _week_delta(session)
    stats.recent_tickets = tickets[:12]
    stats.triage_tickets = sorted(
        stats.triage_tickets,
        key=lambda t: t.created_at or datetime.min,
        reverse=True,
    )

    dept_open: Counter[str] = Counter()
    specialists_open = 0
    for t in open_tickets:
        if t.department_queue == SPECIALISTS_QUEUE:
            specialists_open += 1
            continue
        raw = t.department_queue or "Unassigned"
        dept = canonical_department(raw) if raw != "Unassigned" else raw
        dept_open[dept] += 1

    unassigned_triage = sum(
        1
        for t in stats.triage_tickets
        if (
            t.department_queue == SPECIALISTS_QUEUE or t.status == STATUS_ROUTING_REVIEW
        )
        and not t.assignee_id
        and t.status not in _CLOSED
    )
    triage_agents = max(sum(agents_by_dept.values()), 1)

    def _append_team(name: str, open_count: int, agents: int, *, triage: bool = False) -> None:
        if triage:
            cap = min(100, int(open_count / max(agents * 5, 1) * 100))
            note = (
                f"{unassigned_triage} awaiting assignment"
                if open_count
                else "Queue clear"
            )
        else:
            per_agent = open_count / agents if agents else open_count
            cap = min(100, int(per_agent / 5 * 100))
            note = f"{agents} agents · avg {per_agent:.1f} tickets each"
            if cap >= 80:
                note += " — near limit"
        if cap >= 70:
            stats.near_capacity_teams += 1
        stats.team_loads.append(TeamLoad(name, open_count, agents, cap, note))

    known_depts = set(DEPARTMENT_QUEUES) | set(dept_open.keys()) | set(agents_by_dept.keys())
    known_depts.discard("Unassigned")
    known_depts.discard("General")

    ordered_depts = sorted(
        known_depts,
        key=lambda d: (-dept_open.get(d, 0), display_department(d)),
    )
    for dept in ordered_depts:
        agents = agents_by_dept.get(dept, 0)
        open_count = dept_open.get(dept, 0)
        if open_count == 0 and agents == 0:
            continue
        label = display_department(dept)
        team_name = f"{label} Team" if not label.endswith("Team") else label
        _append_team(team_name, open_count, max(agents, 1))

    _append_team(
        "Routing Specialists (SecOps)",
        specialists_open,
        agents_by_dept.get("SecOps", 1),
        triage=True,
    )

    stats.specialists_open = specialists_open
    requested_ids = [
        row[0]
        for row in session.query(AuditLog.ticket_id)
        .filter(AuditLog.event_type == EVENT_SPECIALIST_REQUESTED)
        .distinct()
        .all()
        if row[0]
    ]
    if requested_ids:
        stats.specialists_routing_resolved = (
            session.query(Ticket)
            .filter(
                Ticket.ticket_id.in_(requested_ids),
                ~Ticket.ticket_id.like("syn-%"),
                Ticket.status.in_(("RESOLVED", "CLOSED")),
            )
            .count()
        )
    else:
        stats.specialists_routing_resolved = 0

    return stats


def _status_bucket(status: str) -> str:
    if status in ("ROUTED", "IN_PROGRESS", "RECEIVED", "SELF_HELP"):
        return "Open"
    if status == "RESOLVED":
        return "Resolved"
    if status == "CLOSED":
        return "Closed"
    if status in ("HUMAN_REVIEW", "ESCALATED"):
        return "In Triage"
    if status == STATUS_ROUTING_REVIEW:
        return "Routing Specialists"
    return "Open"
