"""Demo sign-in credentials — email + shared password for hackathon UI."""

from __future__ import annotations

DEFAULT_DEMO_PASSWORD = "1234"

# Canonical DB emails (lowercase). Display names for reference only.
EMPLOYEE_PORTAL_EMAILS = frozenset(
    {
        "pallavi@user",
        "gajanan@user",
        "imran@user",
        "naveen@user",
        "santhosh@user",
        "requester@demo.local",
    }
)

AGENT_WORKSPACE_EMAILS = frozenset(
    {
        "sree@employee",
        "kiran@employee",
        "subbu@employee",
        "sruthi@employee",
        "meena@employee",
        "shashi@employee",
        "rahul@employee",
        "narsimha@employee",
        "chandana@employee",
        "satya@employee",
        "sagar@employee",
        "priya@employee",
        "admin@employee",
    }
)

ALL_DEMO_EMAILS = EMPLOYEE_PORTAL_EMAILS | AGENT_WORKSPACE_EMAILS


def normalize_email(email: str) -> str:
    return email.strip().lower()


def verify_demo_password(password: str) -> bool:
    return password == DEFAULT_DEMO_PASSWORD
