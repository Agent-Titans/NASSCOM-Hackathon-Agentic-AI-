"""Display names for IntelliQ demo accounts (lowercase email keys)."""

from __future__ import annotations

DEMO_DISPLAY_NAMES: dict[str, str] = {
    # Employee portal
    "pallavi@user": "Pallavi",
    "gajanan@user": "Gajanan",
    "imran@user": "Imran",
    "naveen@user": "Naveen",
    "santhosh@user": "Santhosh",
    # Agent workspace
    "sree@employee": "Sree",
    "subbu@employee": "Subbu",
    "sruthi@employee": "Sruthi",
    "shashi@employee": "Shashi",
    "narsimha@employee": "Narsimha",
    "chandana@employee": "Chandana",
    "satya@employee": "Satya",
    "sagar@employee": "Sagar",
    "admin@employee": "Global System Admin",
}

AGENT_QUEUE_LABELS: dict[str, str] = {
    "sree@employee": "Hardware",
    "subbu@employee": "Software",
    "sruthi@employee": "Software",
    "shashi@employee": "Network",
    "narsimha@employee": "SecOps",
    "chandana@employee": "SecOps",
    "satya@employee": "Access Management",
    "sagar@employee": "DBA",
    "admin@employee": "Admin",
}


def demo_person_name(email: str) -> str:
    key = email.strip().lower()
    if key in DEMO_DISPLAY_NAMES:
        return DEMO_DISPLAY_NAMES[key]
    local = key.split("@")[0]
    return local.replace(".", " ").replace("_", " ").title()
