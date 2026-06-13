import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.config.settings import get_settings
from src.db.models import Ticket, User


class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.smtp_host = self.settings.smtp_host
        self.smtp_port = self.settings.smtp_port
        self.smtp_user = self.settings.smtp_user
        self.smtp_password = self.settings.smtp_password
        self.sender_email = self.settings.sender_email
        self.notification_recipient = self.settings.notification_recipient

    def _get_smtp_server(self):
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        return server

    def send_new_ticket_notification(
        self, ticket: Ticket, user: User, template_path: Path
    ) -> bool:
        if not self.notification_recipient:
            print("Email notification recipient not configured.")
            return False

        try:
            with open(template_path, "r") as f:
                html_template = f.read()

            ticket_id_short = ticket.ticket_id[:8].upper()
            hand_label = {"1": "Self-Help (H1)", "2": "Smart Routing (H2)", "3": "Expert Escalation (H3)"}.get(
                ticket.hand or "", "Pending"
            )
            status_label = {
                "OPEN": "Open",
                "ROUTED": "Routed",
                "IN_PROGRESS": "In Progress",
                "ESCALATED": "Escalated",
                "RESOLVED": "Resolved",
                "CLOSED": "Closed",
            }.get(ticket.status or "", ticket.status or "Open")
            description = (ticket.description_raw or "")[:300]
            created = ticket.created_at.strftime("%a, %-d %b %Y · %-I:%M %p") if ticket.created_at else "N/A"

            replacements = {
                "{{ticket_id}}": ticket.ticket_id,
                "{{ticket_id_short}}": ticket_id_short,
                "{{ticket_title}}": ticket.title or "",
                "{{ticket_description}}": description,
                "{{ticket_status}}": status_label,
                "{{ticket_status_class}}": self._status_css_class(ticket.status),
                "{{ticket_priority}}": (ticket.priority or "N/A").upper(),
                "{{ticket_department}}": ticket.department_queue or "N/A",
                "{{ticket_hand}}": hand_label,
                "{{ticket_urgency}}": (ticket.urgency or "N/A").title(),
                "{{user_name}}": user.email.split("@")[0].title(),
                "{{user_email}}": user.email,
                "{{current_date}}": created,
                "{{sender_email}}": self.sender_email,
            }

            html_content = html_template
            for key, val in replacements.items():
                html_content = html_content.replace(key, val)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"New Ticket Created: INC-{ticket_id_short} - {ticket.title}"
            msg["From"] = self.sender_email
            msg["To"] = self.notification_recipient

            part1 = MIMEText(html_content, "html")
            msg.attach(part1)

            server = self._get_smtp_server()
            server.sendmail(self.sender_email, self.notification_recipient, msg.as_string())
            server.quit()
            print(f"Email notification sent for ticket {ticket.ticket_id} to {self.notification_recipient}")
            return True
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False

    @staticmethod
    def _status_css_class(status: str) -> str:
        return {
            "OPEN": "s-open",
            "ROUTED": "s-open",
            "IN_PROGRESS": "s-triage",
            "ESCALATED": "s-triage",
            "RESOLVED": "s-resolved",
            "CLOSED": "s-closed",
        }.get(status or "", "s-open")
