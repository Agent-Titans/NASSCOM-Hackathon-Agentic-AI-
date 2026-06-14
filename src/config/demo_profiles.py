"""Display names for SAARTHI demo accounts (lowercase email keys)."""

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
    "kiran@employee": "Kiran",
    "vikram@employee": "Vikram",
    "subbu@employee": "Subbu",
    "sruthi@employee": "Sruthi",
    "meena@employee": "Meena",
    "anita@employee": "Anita",
    "shashi@employee": "Shashi",
    "rahul@employee": "Rahul",
    "deepak@employee": "Deepak",
    "narsimha@employee": "Narsimha",
    "chandana@employee": "Chandana",
    "rohan@employee": "Rohan",
    "satya@employee": "Satya",
    "meera@employee": "Meera",
    "sagar@employee": "Sagar",
    "priya@employee": "Priya",
    "arjun@employee": "Arjun",
    "admin@employee": "Global System Admin",
}

AGENT_QUEUE_LABELS: dict[str, str] = {
    "sree@employee": "Infrastructure",
    "kiran@employee": "Infrastructure",
    "vikram@employee": "Infrastructure",
    "subbu@employee": "Application",
    "sruthi@employee": "Application",
    "meena@employee": "Application",
    "anita@employee": "Application",
    "shashi@employee": "Network",
    "rahul@employee": "Network",
    "deepak@employee": "Network",
    "narsimha@employee": "SecOps",
    "chandana@employee": "SecOps",
    "rohan@employee": "SecOps",
    "satya@employee": "Access Management",
    "meera@employee": "Access Management",
    "sagar@employee": "Database",
    "priya@employee": "Database",
    "arjun@employee": "Storage",
    "admin@employee": "Admin",
}


def demo_person_name(email: str) -> str:
    key = email.strip().lower()
    if key in DEMO_DISPLAY_NAMES:
        return DEMO_DISPLAY_NAMES[key]
    local = key.split("@")[0]
    return local.replace(".", " ").replace("_", " ").title()
