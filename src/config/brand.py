"""Product name and copy — single place for UI strings."""

PRODUCT_NAME = "SAARTHI"
ORG_NAME = "SAARTHI Systems"
PRODUCT_ABBREVIATION = (
    "Smart Assignment, Auto-Route, Triage & Handoff Intelligence"
)
TAGLINE = "Every incident finds its path"
DESCRIPTION = TAGLINE

# User-facing Hand labels (not "Hand 1" in primary UI)
HAND_DISPLAY = {
    "1": ("Self-Help", "Steps you can try now", "hand-1"),
    "2": ("Team Assist", "Routed to the right team", "hand-2"),
    "3": ("Specialist", "Expert review", "hand-3"),
}

ROLE_DISPLAY = {
    "requester": "Employee",
    "assignee": "Support",
    "admin": "Admin",
}
