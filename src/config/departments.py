"""Department queue labels — single canonical names for UI and routing."""

from __future__ import annotations

ACCESS_MANAGEMENT = "Access Management"
_LEGACY_IDENTITY = "Identity"

# Canonical assignee / routing queues shown on admin dashboards.
DEPARTMENT_QUEUES: tuple[str, ...] = (
    "Hardware",
    "Software",
    "Network",
    "SecOps",
    ACCESS_MANAGEMENT,
    "DBA",
)


def display_department(name: str | None) -> str:
    """Normalize legacy DB values and return user-facing department label."""
    if not name:
        return "Pending"
    if name == _LEGACY_IDENTITY:
        return ACCESS_MANAGEMENT
    return name


def canonical_department(name: str) -> str:
    """Map legacy stored values to the canonical department queue name."""
    if name == _LEGACY_IDENTITY:
        return ACCESS_MANAGEMENT
    if name == "Storage":
        return "DBA"
    return name


def departments_match(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return canonical_department(left) == canonical_department(right)


def department_queue_aliases(department: str) -> tuple[str, ...]:
    """DB values that belong to the same assignee queue (incl. legacy Identity)."""
    canon = canonical_department(department)
    if canon == ACCESS_MANAGEMENT:
        return (ACCESS_MANAGEMENT, _LEGACY_IDENTITY)
    if canon == "DBA":
        return ("DBA", "Storage")
    return (canon,)
