"""
Department queue names — single source of truth for routing and UI labels.

How routing uses this file:
  1. Classifier outputs a *category* (e.g. "Network", "Security").
  2. CATEGORY_TO_DEPARTMENT maps category → assignee queue in O(1) dict lookup.
  3. canonical_department() normalizes legacy DB strings (Hardware → Infrastructure).
  4. display_department() is what portals show to humans.

Data structures:
  - dict for category → queue (7 categories, 6 operational queues + SecOps)
  - tuple for immutable ordered queue lists shown in dropdowns
"""

from __future__ import annotations

from src.config.specialists import SPECIALISTS_DISPLAY, SPECIALISTS_QUEUE

ACCESS_MANAGEMENT = "Access Management"
_LEGACY_IDENTITY = "Identity"

# Classifier category → assignee / routing queue (hash map, O(1) lookup).
CATEGORY_TO_DEPARTMENT: dict[str, str] = {
    "Infrastructure": "Infrastructure",
    "Application": "Application",
    "Security": "SecOps",
    "Database": "Database",
    "Storage": "Storage",
    "Network": "Network",
    "Access Management": ACCESS_MANAGEMENT,
}

# Legacy queue names stored in SQLite before taxonomy rename.
_LEGACY_DEPARTMENT: dict[str, str] = {
    "Hardware": "Infrastructure",
    "Software": "Application",
    "DBA": "Database",
}

# Canonical assignee / routing queues shown on admin dashboards.
DEPARTMENT_QUEUES: tuple[str, ...] = (
    "Infrastructure",
    "Application",
    "Database",
    "Storage",
    "Network",
    "SecOps",
    ACCESS_MANAGEMENT,
)

# Queues shown in SecOps "Route to department" dropdown (SecOps desk excluded).
OPERATIONAL_DEPARTMENT_QUEUES: tuple[str, ...] = tuple(
    q for q in DEPARTMENT_QUEUES if q != "SecOps"
)
# Frozenset for O(1) membership checks in reroute validators.
OPERATIONAL_DEPARTMENT_SET: frozenset[str] = frozenset(OPERATIONAL_DEPARTMENT_QUEUES)


def display_department(name: str | None) -> str:
    """Normalize legacy DB values and return user-facing department label."""
    if not name:
        return "Pending"
    if name == SPECIALISTS_QUEUE:
        return SPECIALISTS_DISPLAY
    return canonical_department(name)


def canonical_department(name: str) -> str:
    """Map legacy stored values to the canonical department queue name."""
    if name == SPECIALISTS_QUEUE:
        return SPECIALISTS_QUEUE
    if name == _LEGACY_IDENTITY:
        return ACCESS_MANAGEMENT
    return _LEGACY_DEPARTMENT.get(name, name)


def departments_match(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return canonical_department(left) == canonical_department(right)


def department_queue_aliases(department: str) -> tuple[str, ...]:
    """DB values that belong to the same assignee queue (incl. legacy names)."""
    canon = canonical_department(department)
    aliases = {canon}
    if canon == ACCESS_MANAGEMENT:
        aliases.add(_LEGACY_IDENTITY)
    for legacy, target in _LEGACY_DEPARTMENT.items():
        if target == canon:
            aliases.add(legacy)
    return tuple(sorted(aliases))


def department_for_category(category: str) -> str:
    """Route a classifier category to its department queue."""
    return CATEGORY_TO_DEPARTMENT.get(category, "Application")
