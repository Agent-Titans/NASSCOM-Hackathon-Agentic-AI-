"""Auto-assign unowned queue tickets to the best-fit agent on the team."""
from __future__ import annotations

import random
import re
import time
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

_AUTO_ASSIGN_INTERVAL_SEC = 90.0
_last_auto_assign_run: float = 0.0


def reset_auto_assign_throttle() -> None:
    """Clear throttle (tests / forced refresh)."""
    global _last_auto_assign_run
    _last_auto_assign_run = 0.0

from src.config.departments import canonical_department, department_queue_aliases
from src.config.specialists import SPECIALISTS_QUEUE, STATUS_ROUTING_REVIEW
from src.config.settings import get_settings
from src.db.models import AuditLog, Ticket, User
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore

_RAG_TICKET_RE = re.compile(r"ticket=([a-f0-9]{8})")


def _agents_for_department(session: Session, department_queue: str) -> list[User]:
    canon = canonical_department(department_queue)
    queues = set(department_queue_aliases(canon))
    queues.add(canon)
    return (
        session.query(User)
        .filter(User.role == "assignee", User.department.in_(sorted(queues)))
        .order_by(User.email.asc())
        .all()
    )


def _open_assignment_load(session: Session, agent_id: str) -> int:
    return (
        session.query(Ticket)
        .filter(
            Ticket.assignee_id == agent_id,
            Ticket.hand.in_(("2", "3")),
            Ticket.status.notin_(("RESOLVED", "CLOSED")),
        )
        .count()
    )


def _similar_ticket_id_from_audit(session: Session, ticket_id: str) -> Optional[str]:
    """Resolve the RAG-matched ticket id recorded during pipeline routing."""
    row = (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.event_type == "rag_hit",
        )
        .order_by(AuditLog.timestamp.asc())
        .first()
    )
    if not row or not row.details:
        return None
    match = _RAG_TICKET_RE.search(row.details)
    if not match:
        return None
    prefix = match.group(1)
    similar = (
        session.query(Ticket)
        .filter(Ticket.ticket_id.like(f"{prefix}%"))
        .order_by(Ticket.created_at.desc())
        .first()
    )
    return similar.ticket_id if similar else None


def _assignee_who_worked_ticket(session: Session, ticket_id: str) -> Optional[User]:
    """Return the agent who owned a resolved/closed ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket or not ticket.assignee_id:
        return None
    if ticket.status not in ("RESOLVED", "CLOSED"):
        return None
    return session.get(User, ticket.assignee_id)


def _prior_assignee_from_similar(
    session: Session,
    ticket: Ticket,
    agents: list[User],
) -> Optional[User]:
    """Agent who worked a similar ticket on this team, if any."""
    if not agents:
        return None
    allowed = {a.user_id for a in agents}
    dept_queues = set(department_queue_aliases(canonical_department(ticket.department_queue or "")))
    dept_queues.add(canonical_department(ticket.department_queue or ""))

    similar_id = _similar_ticket_id_from_audit(session, ticket.ticket_id)
    if similar_id:
        worker = _assignee_who_worked_ticket(session, similar_id)
        if worker and worker.user_id in allowed and worker.role == "assignee":
            return worker

    # Same department: who resolved tickets that matched the same RAG reference?
    peer_hits = (
        session.query(AuditLog)
        .filter(AuditLog.event_type == "rag_hit", AuditLog.details.like("ticket=%"))
        .all()
    )
    if similar_id:
        prefix = similar_id[:8]
    else:
        prefix = None

    if prefix:
        scores: dict[str, int] = {}
        for hit in peer_hits:
            if not hit.details or prefix not in hit.details:
                continue
            if hit.ticket_id == ticket.ticket_id:
                continue
            prior = session.get(Ticket, hit.ticket_id)
            if not prior or prior.department_queue not in dept_queues:
                continue
            if prior.status not in ("RESOLVED", "CLOSED"):
                continue
            if not prior.assignee_id or prior.assignee_id not in allowed:
                continue
            scores[prior.assignee_id] = scores.get(prior.assignee_id, 0) + 1
        if scores:
            best_id = max(scores, key=lambda uid: (scores[uid], uid))
            worker = session.get(User, best_id)
            if worker:
                return worker

    return None


def _agent_has_capacity(session: Session, agent: User, agents: list[User]) -> bool:
    """True when the agent is not materially busier than the least-loaded peer."""
    if not agents:
        return False
    load = _open_assignment_load(session, agent.user_id)
    min_load = min(_open_assignment_load(session, a.user_id) for a in agents)
    return load <= min_load + 1


def _auto_assign_eligible_at(session: Session, ticket: Ticket) -> datetime:
    """
    When the idle grace window starts.

    Hand 1→2 escalations restart the clock from feedback_escalation time.
    """
    created = ticket.created_at or datetime.utcnow()
    if ticket.hand not in ("2", "3"):
        return created
    esc = (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id == ticket.ticket_id,
            AuditLog.event_type == "feedback_escalation",
        )
        .order_by(AuditLog.timestamp.desc())
        .first()
    )
    if esc and esc.timestamp:
        return max(created, esc.timestamp)
    return created


def is_specialists_desk_ticket(ticket: Ticket) -> bool:
    """SecOps-owned routing review queue — misroutes from any department."""
    return ticket.department_queue == SPECIALISTS_QUEUE or ticket.status == STATUS_ROUTING_REVIEW


def is_triage_ticket(ticket: Ticket) -> bool:
    """Hand 3 / human review — may be owned by any assignee on the triage roster."""
    return (
        ticket.hand == "3"
        or ticket.status in ("HUMAN_REVIEW", "ESCALATED")
        or bool(ticket.escalation_required)
    )


def _all_assignees(session: Session) -> list[User]:
    return (
        session.query(User)
        .filter(User.role == "assignee")
        .order_by(User.email.asc())
        .all()
    )


def pick_least_loaded_among(session: Session, agents: list[User]) -> Optional[User]:
    """Pick randomly among agents within one load tier of the least busy peer."""
    if not agents:
        return None
    loads = {agent.user_id: _open_assignment_load(session, agent.user_id) for agent in agents}
    min_load = min(loads.values())
    tier = [agent for agent in agents if loads[agent.user_id] <= min_load + 1]
    return random.choice(tier)


def pick_triage_agent(session: Session, ticket: Ticket) -> Optional[User]:
    """Any assignee with capacity — not limited to the ticket's department queue."""
    agents = _all_assignees(session)
    if not agents:
        return None

    prior = _prior_assignee_from_similar(session, ticket, agents)
    if prior and _agent_has_capacity(session, prior, agents):
        return prior
    return pick_least_loaded_among(session, agents)


def pick_least_loaded_agent(session: Session, department_queue: str) -> Optional[User]:
    """Choose team member with fewest open Hand 2/3 assignments."""
    agents = _agents_for_department(session, department_queue)
    if not agents:
        return None

    best: Optional[User] = None
    best_load = -1
    for agent in agents:
        load = _open_assignment_load(session, agent.user_id)
        if best is None or load < best_load or (load == best_load and agent.email < best.email):
            best = agent
            best_load = load
    return best


def pick_agent_for_ticket(session: Session, ticket: Ticket) -> Optional[User]:
    """
    Pick assignee: prior worker on a similar ticket if they have capacity,
    otherwise least-loaded team member.
    """
    department = ticket.department_queue or ""
    agents = _agents_for_department(session, department)
    if not agents:
        return None

    prior = _prior_assignee_from_similar(session, ticket, agents)
    if prior and _agent_has_capacity(session, prior, agents):
        return prior
    return pick_least_loaded_agent(session, department)


def assign_escalated_ticket(session: Session, ticket: Ticket) -> bool:
    """
    Assign a Hand 2 ticket immediately after requester escalation (skip grace window).
    """
    if ticket.assignee_id or ticket.hand != "2" or not ticket.department_queue:
        return False
    agent = pick_agent_for_ticket(session, ticket)
    if not agent:
        return False
    store = TicketStore(session)
    audit = AuditLogStore(session)
    store.assign(ticket, agent)
    audit.record(
        ticket,
        "auto_assigned",
        agent="router",
        details=f"assignee={agent.email} dept={ticket.department_queue} reason=h1_feedback_escalation",
    )
    return True


def run_auto_assignments(session: Session, *, force: bool = False) -> int:
    """
    Assign tickets with no owner after the grace window to a team agent.

    Returns the number of tickets auto-assigned this run.
    """
    global _last_auto_assign_run
    now = time.monotonic()
    if not force and (now - _last_auto_assign_run) < _AUTO_ASSIGN_INTERVAL_SEC:
        return 0
    _last_auto_assign_run = now

    settings = get_settings()
    grace = timedelta(minutes=settings.auto_assign_grace_minutes)
    cutoff = datetime.utcnow() - grace

    pool = (
        session.query(Ticket)
        .filter(
            Ticket.assignee_id.is_(None),
            Ticket.status.notin_(("RESOLVED", "CLOSED", "SELF_HELP")),
        )
        .order_by(Ticket.created_at.asc())
        .all()
    )
    candidates: list[Ticket] = []
    for ticket in pool:
        if ticket.hand not in ("2", "3") and not is_triage_ticket(ticket):
            continue
        if not is_triage_ticket(ticket) and not ticket.department_queue:
            continue
        if ticket.hand == "1":
            continue
        if _auto_assign_eligible_at(session, ticket) > cutoff:
            continue
        candidates.append(ticket)
    if not candidates:
        return 0

    store = TicketStore(session)
    audit = AuditLogStore(session)
    assigned = 0

    for ticket in candidates:
        if is_specialists_desk_ticket(ticket):
            agents = _agents_for_department(session, "SecOps")
            agent = pick_least_loaded_among(session, agents)
            reason = f"specialists_desk_{settings.auto_assign_grace_minutes}m"
        elif is_triage_ticket(ticket):
            agents = _all_assignees(session)
            agent = pick_triage_agent(session, ticket)
            prior = _prior_assignee_from_similar(session, ticket, agents)
            reason = f"triage_unassigned_{settings.auto_assign_grace_minutes}m"
            if prior and prior.user_id == agent.user_id:
                reason = f"triage_similar_prior_{settings.auto_assign_grace_minutes}m"
        else:
            dept_agents = _agents_for_department(session, ticket.department_queue or "")
            agent = pick_agent_for_ticket(session, ticket)
            prior = _prior_assignee_from_similar(session, ticket, dept_agents)
            reason = f"unassigned_{settings.auto_assign_grace_minutes}m"
            if prior and agent and prior.user_id == agent.user_id:
                reason = f"similar_ticket_prior_{settings.auto_assign_grace_minutes}m"

        if not agent:
            continue

        store.assign(ticket, agent)
        audit.record(
            ticket,
            "auto_assigned",
            agent="router",
            details=(
                f"assignee={agent.email} "
                f"dept={ticket.department_queue} "
                f"reason={reason}"
            ),
        )
        assigned += 1

    return assigned
