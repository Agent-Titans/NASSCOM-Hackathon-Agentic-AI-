"""
Supervisor agent — weighted score + policy → Hand 1/2/3.

Time: O(1) arithmetic per ticket.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from src.config.settings import get_settings
from src.models.schemas import (
    ClassificationResult,
    ResolutionResult,
    RoutingResult,
    SupervisorDecision,
)


def _hint_to_float(hint: str) -> float:
    return {"high": 0.85, "medium": 0.55, "low": 0.25}.get(hint, 0.5)


@lru_cache(maxsize=1)
def _policy_categories(path: str) -> List[str]:
    rules = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(rules.get("policy_force_hand3_categories", []))


class SupervisorAgent:
    def decide(
        self,
        classification: ClassificationResult,
        resolution: ResolutionResult,
        *,
        sentiment: float = 0.5,
        historical_success: float = 0.5,
    ) -> SupervisorDecision:
        settings = get_settings()
        similarity = resolution.similarity_score

        # LLD formula — O(1)
        c_total = (similarity * 0.6) + (sentiment * 0.2) + (historical_success * 0.2)

        policy_cats = _policy_categories(str(settings.routing_rules_path))
        policy_trigger = None
        escalation = False

        if classification.use_case_category in policy_cats:
            policy_trigger = "security_policy"
            escalation = True
            return SupervisorDecision(
                hand="3",
                c_total=c_total,
                escalation_required=True,
                status="ESCALATED",
                policy_trigger=policy_trigger,
            )

        if resolution.low_grounding and classification.confidence_hint == "low":
            return SupervisorDecision(
                hand="3",
                c_total=c_total,
                escalation_required=True,
                status="HUMAN_REVIEW",
                policy_trigger="low_grounding_and_confidence",
            )

        if resolution.low_grounding:
            # Medium trust — route with assist (Hand 2) even without strong RAG.
            return SupervisorDecision(
                hand="2",
                c_total=c_total,
                escalation_required=False,
                status="ROUTED",
            )

        if c_total >= settings.c_total_hand1:
            return SupervisorDecision(
                hand="1",
                c_total=c_total,
                escalation_required=False,
                status="SELF_HELP",
            )
        if c_total >= settings.c_total_hand2:
            return SupervisorDecision(
                hand="2",
                c_total=c_total,
                escalation_required=False,
                status="ROUTED",
            )

        return SupervisorDecision(
            hand="3",
            c_total=c_total,
            escalation_required=True,
            status="HUMAN_REVIEW",
        )

    def sentiment_from_classification(self, classification: ClassificationResult) -> float:
        """Proxy sentiment until real model — O(1)."""
        return _hint_to_float(classification.confidence_hint)
