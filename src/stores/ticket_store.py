from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.config.departments import department_queue_aliases
from src.db.models import Ticket, User

_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class TicketStore:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(self, user_id: str) -> list[Ticket]:
        return (
            self.session.query(Ticket)
            .filter(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    def list_pending_for_user(self, user_id: str) -> list[Ticket]:
        """Active tickets for employee portal (no resolved/closed lifecycle yet)."""
        return (
            self.session.query(Ticket)
            .filter(Ticket.user_id == user_id)
            .filter(Ticket.status.notin_(("RESOLVED", "CLOSED")))
            .order_by(Ticket.created_at.desc())
            .all()
        )

    def list_for_department(
        self,
        department: str,
        *,
        include_resolved: bool = False,
    ) -> list[Ticket]:
        """Assignee queue: Hand 2 and 3 only (Hand 1 stays with requester)."""
        from src.services.auto_assign_service import run_auto_assignments

        run_auto_assignments(self.session)
        queues = department_queue_aliases(department)
        q = (
            self.session.query(Ticket)
            .filter(
                Ticket.department_queue.in_(queues),
                Ticket.hand.in_(("2", "3")),
            )
        )
        if not include_resolved:
            q = q.filter(Ticket.status.notin_(("RESOLVED", "CLOSED")))
        tickets = q.all()
        return sorted(tickets, key=self._queue_sort_key)

    def department_stats(self, department: str, assignee_id: str) -> dict:
        from src.services.auto_assign_service import run_auto_assignments

        run_auto_assignments(self.session)
        queues = department_queue_aliases(department)
        all_dept = (
            self.session.query(Ticket)
            .filter(
                Ticket.department_queue.in_(queues),
                Ticket.hand.in_(("2", "3")),
            )
            .all()
        )
        tickets = sorted(
            (t for t in all_dept if t.status not in ("RESOLVED", "CLOSED")),
            key=self._queue_sort_key,
        )
        resolved = [t for t in all_dept if t.status == "RESOLVED"]
        unassigned = [t for t in tickets if not t.assignee_id]
        mine = [t for t in tickets if t.assignee_id == assignee_id]
        at_risk = [t for t in tickets if self.sla_at_risk(t)]
        escalations = [
            t for t in tickets if t.hand == "3" or t.escalation_required
        ]
        return {
            "total": len(tickets),
            "unassigned": len(unassigned),
            "mine": len(mine),
            "at_risk": len(at_risk),
            "escalations": len(escalations),
            "resolved": len(resolved),
            "tickets": tickets,
            "resolved_tickets": resolved,
        }

    def get(self, ticket_id: str) -> Optional[Ticket]:
        return self.session.get(Ticket, ticket_id)

    def create(
        self,
        user: User,
        title: str,
        description: str,
        urgency: str = "medium",
    ) -> Ticket:
        ticket = Ticket(
            user_id=user.user_id,
            title=title,
            description_raw=description,
            urgency=urgency,
            status="RECEIVED",
        )
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def assign(self, ticket: Ticket, assignee: User) -> Ticket:
        ticket.assignee_id = assignee.user_id
        if ticket.status in ("ROUTED", "HUMAN_REVIEW", "ESCALATED"):
            ticket.status = "IN_PROGRESS"
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def release(self, ticket: Ticket) -> Ticket:
        ticket.assignee_id = None
        if ticket.status == "IN_PROGRESS":
            ticket.status = "ROUTED" if ticket.hand == "2" else "HUMAN_REVIEW"
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def resolve(self, ticket: Ticket) -> Ticket:
        ticket.status = "RESOLVED"
        self.session.commit()
        self.session.refresh(ticket)
        from src.services.historical_success_service import invalidate_historical_cache
        from src.services.process_cache import invalidate_retrieval_cache
        from src.services.ticket_retrieval import mark_resolved_ticket_for_index

        mark_resolved_ticket_for_index(ticket.ticket_id)
        invalidate_retrieval_cache()
        invalidate_historical_cache()
        return ticket

    def update_hand(
        self,
        ticket: Ticket,
        *,
        hand: str,
        confidence: float,
        status: str,
        department_queue: Optional[str] = None,
        priority: Optional[str] = None,
        sla_hours: Optional[int] = None,
        escalation_required: bool = False,
        sanitized: Optional[str] = None,
    ) -> Ticket:
        ticket.hand = hand
        ticket.confidence = confidence
        ticket.status = status
        ticket.department_queue = department_queue
        ticket.priority = priority
        ticket.sla_hours = sla_hours
        ticket.escalation_required = escalation_required
        if sanitized is not None:
            ticket.description_sanitized = sanitized
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    @staticmethod
    def sla_deadline(ticket: Ticket) -> Optional[datetime]:
        if not ticket.sla_hours or not ticket.created_at:
            return None
        return ticket.created_at + timedelta(hours=ticket.sla_hours)

    @staticmethod
    def sla_remaining_hours(ticket: Ticket) -> Optional[float]:
        deadline = TicketStore.sla_deadline(ticket)
        if not deadline:
            return None
        return (deadline - datetime.utcnow()).total_seconds() / 3600

    @staticmethod
    def sla_at_risk(ticket: Ticket, threshold_ratio: float = 0.25) -> bool:
        remaining = TicketStore.sla_remaining_hours(ticket)
        if remaining is None or ticket.status in ("RESOLVED", "CLOSED"):
            return False
        if remaining <= 0:
            return True
        if not ticket.sla_hours:
            return False
        return remaining <= ticket.sla_hours * threshold_ratio

    @staticmethod
    def sla_label(ticket: Ticket) -> tuple[str, str]:
        remaining = TicketStore.sla_remaining_hours(ticket)
        if remaining is None:
            return "—", "sla-ok"
        if remaining <= 0:
            hrs = abs(int(remaining))
            return f"Overdue {hrs}h", "sla-breach"
        if TicketStore.sla_at_risk(ticket):
            return f"{int(remaining)}h left", "sla-risk"
        return f"{int(remaining)}h left", "sla-ok"

    def _queue_sort_key(self, ticket: Ticket) -> tuple:
        pri = _PRIORITY_ORDER.get(ticket.priority or "P2", 9)
        remaining = self.sla_remaining_hours(ticket)
        sla_key = remaining if remaining is not None else 9999
        return (pri, sla_key, -ticket.created_at.timestamp())
