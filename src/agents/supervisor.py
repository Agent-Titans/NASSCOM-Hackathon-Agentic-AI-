"""
Supervisor agent — weighted score + policy → Hand 1/2/3.

Time: O(1) arithmetic per ticket.

LLD: #supervisor-agent — c_total formula and bands; policy overrides from
config/routing_rules.json (mode: strict_lld | demo).
"""
from __future__ import annotations

from src.config.rag_policy import blocks_hand1_similarity
from src.config.settings import get_settings
from src.config.supervisor_policy import get_supervisor_policy, matches_hand1_playbook
from src.models.schemas import (
    ClassificationResult,
    ResolutionResult,
    SupervisorDecision,
)


def _hint_to_float(hint: str) -> float:
    return {"high": 0.85, "medium": 0.55, "low": 0.25}.get(hint, 0.5)


def _cap_hand(hand: str, max_hand: str) -> str:
    return str(min(int(hand), int(max_hand)))


def _status_for_hand(hand: str, *, escalation: bool) -> str:
    if hand == "1":
        return "SELF_HELP"
    if hand == "2":
        return "ROUTED"
    return "ESCALATED" if escalation else "HUMAN_REVIEW"


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
        policy = get_supervisor_policy()
        similarity = resolution.similarity_score

        # LLD formula — O(1)
        c_total = (similarity * 0.6) + (sentiment * 0.2) + (historical_success * 0.2)

        if classification.use_case_category in policy.force_hand3_categories:
            return SupervisorDecision(
                hand="3",
                c_total=c_total,
                escalation_required=True,
                status="ESCALATED",
                policy_trigger="security_policy",
            )

        if resolution.low_grounding:
            hand = policy.low_grounding_hand
            return SupervisorDecision(
                hand=hand,
                c_total=c_total,
                escalation_required=hand == "3",
                status=_status_for_hand(hand, escalation=hand == "3"),
                policy_trigger="low_grounding",
            )

        if matches_hand1_playbook(
            category=classification.use_case_category,
            similarity=similarity,
            low_grounding=resolution.low_grounding,
        ):
            return SupervisorDecision(
                hand="1",
                c_total=c_total,
                escalation_required=False,
                status="SELF_HELP",
                policy_trigger="hand1_playbook",
            )

        if c_total >= settings.c_total_hand1:
            hand = "1"
            escalation = False
        elif c_total >= settings.c_total_hand2:
            hand = "2"
            escalation = False
        else:
            hand = "3"
            escalation = True

        status = _status_for_hand(hand, escalation=escalation)

        if policy.apply_similarity_hand1_cap and blocks_hand1_similarity(similarity):
            hand = _cap_hand(hand, "2")
            status = "ROUTED"
            escalation = False

        return SupervisorDecision(
            hand=hand,
            c_total=c_total,
            escalation_required=escalation,
            status=status,
        )

    def sentiment_from_classification(self, classification: ClassificationResult) -> float:
        """Proxy sentiment until real model — O(1)."""
        return _hint_to_float(classification.confidence_hint)
