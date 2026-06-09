"""Shared ticket queue/detail display helpers — aligned with LLD (status + Hand)."""
from __future__ import annotations

import html

from sqlalchemy.orm import Session

from src.db.models import Ticket, User

_DISPLAY_NAMES = {
    "requester@demo.local": "Karan Joshi",
    "emily.reed@demo.local": "Emily Reed",
    "james.wu@demo.local": "James Wu",
    "sarah.kim@demo.local": "Sarah Kim",
    "michael.brown@demo.local": "Michael Brown",
    "hardware@demo.local": "Alex Chen",
    "software@demo.local": "Marcus Lee",
    "secops@demo.local": "Sam Ortiz",
    "network@demo.local": "Priya Nair",
    "identity@demo.local": "Jordan Kim",
    "dba@demo.local": "Riley Park",
    "storage@demo.local": "Casey Morgan",
}


def person_name(email: str) -> str:
    if email in _DISPLAY_NAMES:
        return _DISPLAY_NAMES[email]
    local = email.split("@")[0]
    return local.replace(".", " ").replace("_", " ").title()


def department_label(ticket: Ticket) -> str:
    """LLD home list: status surface — department queue for routed work."""
    if ticket.department_queue:
        return ticket.department_queue
    hand = ticket.hand or ""
    if hand == "1":
        return "Self-service"
    if ticket.status == "RESOLVED":
        return "Closed"
    return "Pending"


def hand_routing_label(ticket: Ticket) -> str:
    """LLD home list: selected Hand (1/2/3)."""
    hand = ticket.hand or ""
    if hand in ("1", "2", "3"):
        return f"H{hand}"
    return "—"


def assignee_name(session: Session, ticket: Ticket) -> str:
    if not ticket.assignee_id:
        return "Unassigned"
    assignee = session.get(User, ticket.assignee_id)
    if not assignee:
        return "Unassigned"
    return person_name(assignee.email)


def dept_chip_class(ticket: Ticket) -> str:
    if ticket.department_queue:
        return "portal-chip portal-chip-status-info"
    if ticket.hand == "1":
        return "portal-chip portal-chip-status-ok"
    return "portal-chip portal-chip-status"


def hand_chip_class(hand: str) -> str:
    if hand == "1":
        return "portal-chip portal-chip-hand-1"
    if hand == "2":
        return "portal-chip portal-chip-hand-2"
    if hand == "3":
        return "portal-chip portal-chip-hand"
    return "portal-chip portal-chip-status"


def chip_html(css_class: str, label: str) -> str:
    return f'<span class="{css_class}">{html.escape(label)}</span>'
