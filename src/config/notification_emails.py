"""Map portal demo accounts → real Gmail addresses for outbound notifications only."""

from __future__ import annotations

import re

# Outbound notification inboxes (not used for portal login)
REQUESTER_NOTIFICATION_EMAIL = "jkaran1694@gmail.com"
ASSIGNEE_NOTIFICATION_EMAIL = "manyamiragavarapu@gmail.com"
SECOPS_NOTIFICATION_EMAIL = "nchary05@gmail.com"

_SECOPS_PORTAL_EMAILS = frozenset(
    {
        "narsimha@employee",
        "chandana@employee",
        "rohan@employee",
    }
)

_CONTACT_EMAIL_RE = re.compile(
    r"(?i)(?:contact\s+email|email)\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
)


def extract_contact_email(description: str | None) -> str | None:
    if not description:
        return None
    match = _CONTACT_EMAIL_RE.search(description)
    return match.group(1).strip().lower() if match else None


def requester_notification_email(portal_email: str, description: str | None = None) -> str:
    """Employee portal requester — prefer contact email from ticket body."""
    contact = extract_contact_email(description)
    if contact and not contact.endswith("@user") and not contact.endswith("@employee"):
        return contact
    if portal_email.endswith("@user") or portal_email.endswith("@demo.local"):
        return REQUESTER_NOTIFICATION_EMAIL
    return REQUESTER_NOTIFICATION_EMAIL


def assignee_notification_email(portal_email: str, department: str | None = None) -> str:
    """Agent assignee — SecOps queue uses dedicated inbox."""
    key = portal_email.strip().lower()
    if key in _SECOPS_PORTAL_EMAILS or (department or "").strip() == "SecOps":
        return SECOPS_NOTIFICATION_EMAIL
    if key.endswith("@employee"):
        return ASSIGNEE_NOTIFICATION_EMAIL
    return ASSIGNEE_NOTIFICATION_EMAIL
