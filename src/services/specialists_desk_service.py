"""
Routing Specialists desk — SecOps team fixes AI misroutes in one hop.

Flow (agent portal):
  1. Dept agent clicks Route → ticket moves to Specialists queue (hand unchanged).
  2. SecOps reviews Routing context (original dept, reason, requester).
  3. SecOps either assigns as security work OR picks target dept + Route.

Policy:
  - One-hop only: already_rerouted_from_specialists() blocks second reroute.
  - OPERATIONAL_DEPARTMENT_SET validates target queue in O(1).

Audit trail: EVENT_SPECIALIST_* rows in audit_log.details JSON.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.config.departments import (
    OPERATIONAL_DEPARTMENT_SET,
    canonical_department,
    departments_match,
    display_department,
)
from src.config.specialists import (
    EVENT_SPECIALIST_KEPT_SECOPS,
    EVENT_SPECIALIST_REROUTED,
    EVENT_SPECIALIST_REQUESTED,
    MIN_REASON_CHARS,
    SPECIALISTS_QUEUE,
    STATUS_ROUTING_REVIEW,
)
from src.db.models import AuditLog, Ticket, User
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore


def is_specialists_ticket(ticket: Ticket) -> bool:
    return ticket.department_queue == SPECIALISTS_QUEUE or ticket.status == STATUS_ROUTING_REVIEW


def can_request_specialist(ticket: Ticket, user: User) -> bool:
    if ticket.status in ("RESOLVED", "CLOSED"):
        return False
    if is_specialists_ticket(ticket):
        return False
    if ticket.hand not in ("2", "3"):
        return False
    dept = user.department or ""
    if not departments_match(ticket.department_queue, dept):
        return False
    return True


def can_employee_request_route_review(ticket: Ticket, user: User) -> bool:
    """Requester may ask SecOps Routing Specialists to review AI routing."""
    if ticket.user_id != user.user_id:
        return False
    if ticket.status in ("RESOLVED", "CLOSED"):
        return False
    if is_specialists_ticket(ticket):
        return False
    return True


def _parse_audit_json(details: str | None) -> dict:
    if not details:
        return {}
    try:
        return json.loads(details)
    except json.JSONDecodeError:
        return {"reason": details}


def get_specialist_context(session: Session, ticket_id: str) -> dict:
    """Original AI route + agent reason from audit trail."""
    rows = (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.event_type.in_((EVENT_SPECIALIST_REQUESTED, EVENT_SPECIALIST_REROUTED)),
        )
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    ctx: dict = {
        "original_department": None,
        "original_hand": None,
        "reason": None,
        "requested_by": None,
        "rerouted_to": None,
        "rerouted_by": None,
    }
    for row in rows:
        payload = _parse_audit_json(row.details)
        if row.event_type == EVENT_SPECIALIST_REQUESTED:
            ctx["original_department"] = payload.get("from_dept")
            ctx["original_hand"] = payload.get("from_hand")
            ctx["reason"] = payload.get("reason")
            ctx["requested_by"] = row.agent
        elif row.event_type == EVENT_SPECIALIST_REROUTED:
            ctx["rerouted_to"] = payload.get("to_dept")
            ctx["rerouted_by"] = row.agent
    return ctx


def already_rerouted_from_specialists(session: Session, ticket_id: str) -> bool:
    return (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.event_type == EVENT_SPECIALIST_REROUTED,
        )
        .count()
        > 0
    )


def request_specialist_review(
    session: Session,
    ticket: Ticket,
    user: User,
    reason: str,
) -> tuple[bool, str]:
    reason = (reason or "").strip()
    if len(reason) < MIN_REASON_CHARS:
        return False, f"Please enter at least {MIN_REASON_CHARS} characters explaining the misroute."
    if not can_request_specialist(ticket, user):
        return False, "This ticket cannot be sent to the Routing Specialists desk."

    from_dept = canonical_department(ticket.department_queue or user.department or "")
    from_hand = ticket.hand or "2"
    ticket.assignee_id = None
    ticket.department_queue = SPECIALISTS_QUEUE
    ticket.status = STATUS_ROUTING_REVIEW
    session.commit()
    session.refresh(ticket)

    AuditLogStore(session).record(
        ticket,
        EVENT_SPECIALIST_REQUESTED,
        agent=user.email,
        details=json.dumps(
            {
                "from_dept": from_dept,
                "from_hand": from_hand,
                "reason": reason,
            }
        ),
    )
    return True, "Routed to SecOps-operated Routing Specialists desk."


def request_employee_route_review(
    session: Session,
    ticket: Ticket,
    user: User,
    reason: str,
) -> tuple[bool, str]:
    """Employee-owned ticket → SecOps Routing Specialists desk with reason."""
    reason = (reason or "").strip()
    if len(reason) < MIN_REASON_CHARS:
        return False, f"Please enter at least {MIN_REASON_CHARS} characters explaining the routing concern."
    if not can_employee_request_route_review(ticket, user):
        return False, "This ticket cannot be sent for SecOps routing review."

    from_dept = canonical_department(ticket.department_queue or "")
    from_hand = ticket.hand or "2"
    ticket.assignee_id = None
    ticket.department_queue = SPECIALISTS_QUEUE
    ticket.status = STATUS_ROUTING_REVIEW
    session.commit()
    session.refresh(ticket)

    AuditLogStore(session).record(
        ticket,
        EVENT_SPECIALIST_REQUESTED,
        agent=user.email,
        details=json.dumps(
            {
                "from_dept": from_dept,
                "from_hand": from_hand,
                "reason": reason,
                "requested_by_role": "requester",
            }
        ),
    )
    return True, "Routed to SecOps-operated Routing Specialists desk for review."


def reroute_from_specialists(
    session: Session,
    ticket: Ticket,
    user: User,
    target_department: str,
) -> tuple[bool, str]:
    if user.department != "SecOps":
        return False, "Only SecOps routing specialists can confirm department routes."
    if not is_specialists_ticket(ticket):
        return False, "Ticket is not in the Routing Specialists queue."
    if already_rerouted_from_specialists(session, ticket.ticket_id):
        return False, "This ticket was already rerouted from the specialists desk (one-hop policy)."

    target = canonical_department(target_department)
    if target not in OPERATIONAL_DEPARTMENT_SET:
        return False, "Choose a valid department queue."

    ticket.department_queue = target
    ticket.status = "ROUTED"
    ticket.assignee_id = None
    session.commit()
    session.refresh(ticket)

    AuditLogStore(session).record(
        ticket,
        EVENT_SPECIALIST_REROUTED,
        agent=user.email,
        details=json.dumps({"to_dept": target}),
    )
    return True, f"Rerouted to {target} queue."


def reroute_secops_operational(
    session: Session,
    ticket: Ticket,
    user: User,
    target_department: str,
) -> tuple[bool, str]:
    """SecOps agent transfers an operational SecOps-queue ticket to another department."""
    if user.department != "SecOps":
        return False, "Only SecOps agents can route from the SecOps queue."
    if is_specialists_ticket(ticket):
        return False, "Use the routing specialists desk flow for this ticket."
    if not departments_match(ticket.department_queue, "SecOps"):
        return False, "Ticket is not on the SecOps queue."
    if ticket.status in ("RESOLVED", "CLOSED"):
        return False, "Ticket is already closed."

    target = canonical_department(target_department)
    if target not in OPERATIONAL_DEPARTMENT_SET:
        return False, "Choose a valid department queue."

    ticket.department_queue = target
    ticket.status = "ROUTED"
    ticket.assignee_id = None
    session.commit()
    session.refresh(ticket)

    AuditLogStore(session).record(
        ticket,
        EVENT_SPECIALIST_REROUTED,
        agent=user.email,
        details=json.dumps({"to_dept": target, "from": "SecOps"}),
    )
    return True, f"Rerouted to {display_department(target)} queue."


def keep_specialist_ticket_in_secops(
    session: Session,
    ticket: Ticket,
    user: User,
) -> tuple[bool, str]:
    """SecOps keeps a routing-desk ticket as a security incident."""
    if user.department != "SecOps":
        return False, "Only SecOps can take routing desk tickets."
    if ticket.status in ("RESOLVED", "CLOSED"):
        return False, "Ticket is already closed."
    if ticket.department_queue != SPECIALISTS_QUEUE:
        return False, "Ticket is not on the Routing Specialists desk."

    ticket.department_queue = "SecOps"
    ticket.assignee_id = user.user_id
    ticket.status = "HUMAN_REVIEW" if ticket.hand == "3" else "IN_PROGRESS"
    session.commit()
    session.refresh(ticket)

    AuditLogStore(session).record(
        ticket,
        EVENT_SPECIALIST_KEPT_SECOPS,
        agent=user.email,
        details=json.dumps({"hand": ticket.hand}),
    )
    return True, "Assigned to you on SecOps queue."


def list_specialists_history(session: Session, *, limit: int = 30) -> list[Ticket]:
    """Resolved/closed live tickets that went through the routing specialists desk."""
    requested_rows = (
        session.query(AuditLog.ticket_id)
        .filter(AuditLog.event_type == EVENT_SPECIALIST_REQUESTED)
        .distinct()
        .all()
    )
    ticket_ids = [row[0] for row in requested_rows if row[0]]
    if not ticket_ids:
        return []

    rows = (
        session.query(Ticket)
        .filter(
            Ticket.ticket_id.in_(ticket_ids),
            ~Ticket.ticket_id.like("syn-%"),
            Ticket.status.in_(("RESOLVED", "CLOSED")),
        )
        .all()
    )
    store = TicketStore(session)
    return sorted(
        rows,
        key=lambda t: t.created_at or datetime.min,
        reverse=True,
    )[:limit]


def list_specialists_queue(session: Session) -> list[Ticket]:
    from src.services.auto_assign_service import run_auto_assignments

    run_auto_assignments(session)
    rows = (
        session.query(Ticket)
        .filter(
            Ticket.department_queue == SPECIALISTS_QUEUE,
            Ticket.status.notin_(("RESOLVED", "CLOSED")),
        )
        .all()
    )
    store = TicketStore(session)
    return sorted(rows, key=store._queue_sort_key)
