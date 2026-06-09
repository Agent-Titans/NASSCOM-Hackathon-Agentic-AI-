"""
Router agent — deterministic O(1) hash-map lookups from routing_rules.json.

No LLM — predictable for audit and Nascom fairness.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.config.settings import get_settings
from src.models.schemas import ClassificationResult, RoutingResult


@lru_cache(maxsize=1)
def _load_rules(path: str) -> Dict[str, Any]:
    """Load JSON once per process — O(file size), then cached."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


class RouterAgent:
    def route(self, classification: ClassificationResult, urgency: str) -> RoutingResult:
        rules = _load_rules(str(get_settings().routing_rules_path))
        dept_map: Dict[str, str] = rules.get("category_to_department", {})
        urgency_map: Dict[str, Dict[str, Any]] = rules.get("urgency_to_priority", {})

        # O(1) dict get — default queue if category missing
        department = dept_map.get(
            classification.use_case_category, "General"
        )
        urg = urgency if urgency in urgency_map else "medium"
        pri_block = urgency_map.get(urg, {"priority": "P1", "sla_hours": 24})

        return RoutingResult(
            department_queue=department,
            priority=str(pri_block.get("priority", "P1")),
            sla_hours=int(pri_block.get("sla_hours", 24)),
        )
