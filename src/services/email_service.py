"""SMTP email delivery for ticket lifecycle notifications."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.config.settings import get_settings
from src.db.models import Ticket, User

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(
            self.settings.email_notifications_enabled
            and self.settings.smtp_host
            and self.settings.smtp_user
            and self.settings.smtp_password
            and self.settings.sender_email
        )

    def _get_smtp_server(self) -> smtplib.SMTP:
        server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
        server.starttls()
        server.login(self.settings.smtp_user, self.settings.smtp_password)
        return server

    def send_ticket_notification(
        self,
        *,
        ticket: Ticket,
        recipient: str,
        subject: str,
        headline: str,
        subheadline: str,
        footer_note: str,
        user: User | None = None,
    ) -> bool:
        if not self.enabled:
            logger.debug("Email notifications disabled — skip %s", subject)
            return False
        if not recipient:
            logger.warning("No recipient for ticket %s notification", ticket.ticket_id)
            return False

        template_path = _TEMPLATES_DIR / "ticket_notification.html"
        if not template_path.exists():
            logger.error("Missing email template %s", template_path)
            return False

        try:
            html_template = template_path.read_text(encoding="utf-8")
            ticket_id_short = ticket.ticket_id[:8].upper()
            hand_label = {
                "1": "Self-Help (H1)",
                "2": "Smart Routing (H2)",
                "3": "Expert Escalation (H3)",
            }.get(ticket.hand or "", "Pending")
            status_label = {
                "RECEIVED": "Open",
                "OPEN": "Open",
                "ROUTED": "Routed",
                "IN_PROGRESS": "In Progress",
                "HUMAN_REVIEW": "In Review",
                "ESCALATED": "Escalated",
                "ROUTING_REVIEW": "Routing Review",
                "RESOLVED": "Resolved",
                "CLOSED": "Closed",
                "SELF_HELP": "Self-Help",
            }.get(ticket.status or "", ticket.status or "Open")
            description = (ticket.description_sanitized or ticket.description_raw or "")[:300]
            created = (
                ticket.created_at.strftime("%a, %d %b %Y · %I:%M %p")
                if ticket.created_at
                else "N/A"
            )
            display_name = (
                user.email.split("@")[0].title()
                if user
                else recipient.split("@")[0].title()
            )

            replacements = {
                "{{headline}}": headline,
                "{{subheadline}}": subheadline,
                "{{footer_note}}": footer_note,
                "{{ticket_id}}": ticket.ticket_id,
                "{{ticket_id_short}}": ticket_id_short,
                "{{ticket_title}}": ticket.title or "",
                "{{ticket_description}}": description,
                "{{ticket_status}}": status_label,
                "{{ticket_priority}}": (ticket.priority or "N/A").upper(),
                "{{ticket_department}}": ticket.department_queue or "N/A",
                "{{ticket_hand}}": hand_label,
                "{{ticket_urgency}}": (ticket.urgency or "N/A").title(),
                "{{user_name}}": display_name,
                "{{user_email}}": recipient,
                "{{current_date}}": created,
                "{{sender_email}}": self.settings.sender_email,
            }

            html_content = html_template
            for key, val in replacements.items():
                html_content = html_content.replace(key, val)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.settings.sender_email
            msg["To"] = recipient
            msg.attach(MIMEText(html_content, "html"))

            server = self._get_smtp_server()
            server.sendmail(self.settings.sender_email, recipient, msg.as_string())
            server.quit()
            logger.info("Email sent: %s → %s", subject, recipient)
            return True
        except Exception as exc:
            logger.warning("Failed to send email (%s): %s", subject, exc)
            return False
