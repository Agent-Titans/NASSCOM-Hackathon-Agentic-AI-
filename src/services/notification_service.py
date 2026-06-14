"""
Notification service — ticket lifecycle emails + audit logging.

Emails are OFF by default (EMAIL_NOTIFICATIONS_ENABLED=false).
Portal logins stay on demo @user / @employee addresses.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from src.config.notification_emails import (
    assignee_notification_email,
    requester_notification_email,
)
from src.db.models import Ticket, User
from src.models.schemas import SupervisorDecision
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self._email = EmailService()

    def send_hand_message(
        self, ticket_id: str, decision: SupervisorDecision, requester_email: str
    ) -> None:
        """Legacy hook — pipeline completion also triggers ticket_opened email."""
        hand_names = {"1": "self-help steps", "2": "team routing", "3": "specialist review"}
        msg = hand_names.get(decision.hand, "update")
        logger.info(
            "Notify %s | ticket=%s | Hand %s (%s)",
            requester_email,
            ticket_id,
            decision.hand,
            msg,
        )

    def notify_ticket_opened(self, session: Session, ticket: Ticket) -> None:
        requester = session.get(User, ticket.user_id)
        if not requester:
            return
        recipient = requester_notification_email(
            requester.email, ticket.description_raw
        )
        short = ticket.ticket_id[:8].upper()
        self._email.send_ticket_notification(
            ticket=ticket,
            recipient=recipient,
            subject=f"Ticket Opened: INC-{short} — {ticket.title}",
            headline="Your ticket has been opened.",
            subheadline=f"INC-{short} · {ticket.title} · Routed to {ticket.department_queue or 'queue'}",
            footer_note=(
                f"This email was sent to {recipient} because ticket INC-{short} "
                "was submitted on the employee portal."
            ),
            user=requester,
        )

    def notify_ticket_closed(self, session: Session, ticket: Ticket) -> None:
        requester = session.get(User, ticket.user_id)
        if not requester:
            return
        recipient = requester_notification_email(
            requester.email, ticket.description_raw
        )
        short = ticket.ticket_id[:8].upper()
        self._email.send_ticket_notification(
            ticket=ticket,
            recipient=recipient,
            subject=f"Ticket Closed: INC-{short} — {ticket.title}",
            headline="Your ticket has been closed.",
            subheadline=f"INC-{short} · {ticket.title} · Status: Resolved",
            footer_note=(
                f"This email was sent to {recipient} because ticket INC-{short} "
                "is now closed. Submit a new request if you need further help."
            ),
            user=requester,
        )

    def notify_ticket_assigned(
        self, session: Session, ticket: Ticket, assignee: User
    ) -> None:
        recipient = assignee_notification_email(
            assignee.email, assignee.department
        )
        short = ticket.ticket_id[:8].upper()
        self._email.send_ticket_notification(
            ticket=ticket,
            recipient=recipient,
            subject=f"Ticket Assigned: INC-{short} — {ticket.title}",
            headline="A ticket has been assigned to you.",
            subheadline=(
                f"INC-{short} · {ticket.title} · "
                f"{ticket.department_queue or 'Queue'} team"
            ),
            footer_note=(
                f"This email was sent to {recipient} because INC-{short} "
                f"was assigned to {assignee.email} in the agent workspace."
            ),
            user=assignee,
        )

    def notify_ticket_resolved(
        self, session: Session, ticket: Ticket, assignee: User | None = None
    ) -> None:
        if assignee:
            recipient = assignee_notification_email(
                assignee.email, assignee.department
            )
            short = ticket.ticket_id[:8].upper()
            self._email.send_ticket_notification(
                ticket=ticket,
                recipient=recipient,
                subject=f"Ticket Resolved: INC-{short} — {ticket.title}",
                headline="You marked a ticket as resolved.",
                subheadline=f"INC-{short} · {ticket.title} · Thank you for closing the loop",
                footer_note=(
                    f"This email was sent to {recipient} confirming INC-{short} "
                    "was resolved in the agent workspace."
                ),
                user=assignee,
            )
