"""Encode/decode resolution steps for SQLite (requester + assignee audiences)."""
from __future__ import annotations

import json
from typing import List, Optional, Tuple

_SCHEMA_JUNK = frozenset(
    {"v", "requester", "assignee", "steps_requester", "steps_assignee"}
)


def _coerce_step_list(value: object, *, prefer: str = "requester") -> List[str]:
    """Normalize a value to a list of non-empty step strings."""
    if isinstance(value, dict) and value.get("v") == 2:
        if prefer == "assignee":
            value = value.get("assignee") or value.get("requester")
        else:
            value = value.get("requester") or value.get("assignee")
    if not isinstance(value, list):
        return []
    steps: List[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                steps.append(text)
    return steps


def is_schema_junk_steps(steps: List[str]) -> bool:
    """True when steps are JSON field names, not real instructions."""
    if not steps:
        return True
    normalized = {s.strip().lower() for s in steps}
    return normalized.issubset(_SCHEMA_JUNK)


def encode_steps(
    steps: List[str],
    *,
    steps_requester: Optional[List[str]] = None,
    steps_assignee: Optional[List[str]] = None,
) -> str:
    """Persist steps; dual-audience when rewrite produced both lists."""
    req = _coerce_step_list(steps_requester) or _coerce_step_list(steps)
    asn = _coerce_step_list(steps_assignee)
    if is_schema_junk_steps(req):
        req = []
    if is_schema_junk_steps(asn):
        asn = []
    if not req and not asn:
        return "[]"
    if asn and asn != req:
        return json.dumps({"v": 2, "requester": req, "assignee": asn})
    return json.dumps(req or asn)


def decode_steps(raw: str | None) -> Tuple[List[str], List[str]]:
    """Return (requester_steps, assignee_steps). Assignee falls back to requester."""
    if not raw:
        return [], []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return [], []
    if isinstance(data, dict) and data.get("v") == 2:
        req = _coerce_step_list(data.get("requester"))
        asn = _coerce_step_list(data.get("assignee")) or req
        if is_schema_junk_steps(req) and not is_schema_junk_steps(asn):
            req = asn
        elif is_schema_junk_steps(asn) and not is_schema_junk_steps(req):
            asn = req
        return req, asn
    if isinstance(data, list):
        steps = _coerce_step_list(data)
        if is_schema_junk_steps(steps):
            return [], []
        return steps, steps
    return [], []
