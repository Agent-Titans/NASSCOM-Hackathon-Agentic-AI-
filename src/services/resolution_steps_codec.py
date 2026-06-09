"""Encode/decode resolution steps for SQLite (requester + assignee audiences)."""
from __future__ import annotations

import json
from typing import List, Optional, Tuple


def encode_steps(
    steps: List[str],
    *,
    steps_requester: Optional[List[str]] = None,
    steps_assignee: Optional[List[str]] = None,
) -> str:
    """Persist steps; dual-audience when rewrite produced both lists."""
    req = steps_requester or steps
    asn = steps_assignee
    if asn and asn != req:
        return json.dumps({"v": 2, "requester": req, "assignee": asn})
    return json.dumps(req)


def decode_steps(raw: str | None) -> Tuple[List[str], List[str]]:
    """Return (requester_steps, assignee_steps). Assignee falls back to requester."""
    if not raw:
        return [], []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return [], []
    if isinstance(data, dict) and data.get("v") == 2:
        req = list(data.get("requester") or [])
        asn = list(data.get("assignee") or req)
        return req, asn
    if isinstance(data, list):
        return data, data
    return [], []
