"""
RAG trust gate — single place that decides if a retrieval hit may drive routing.

Weak or risky matches are logged for audit but must not override classification,
resolution steps, or Hand selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.config.settings import get_settings
from src.models.schemas import SimilarTicketMatch


@dataclass(frozen=True)
class RagGateDecision:
    """Outcome of evaluating a raw Chroma/keyword retrieval hit."""

    raw: Optional[SimilarTicketMatch]
    trusted: Optional[SimilarTicketMatch]
    reason: str  # trusted | no_match | below_medium | hand3_requires_high


def evaluate_rag_match(similar: Optional[SimilarTicketMatch]) -> RagGateDecision:
    """
    Decide whether a retrieval hit is strong enough to influence the pipeline.

    Rules (applied in order):
    1. No match → nothing trusted
    2. Score < rag_sim_medium (0.55) → reject (too weak)
    3. Hand 3 corpus/ticket and score < rag_sim_high (0.70) → reject (triage playbooks
       must not win on loose keyword overlap)
    4. Otherwise → trusted
    """
    if similar is None:
        return RagGateDecision(raw=None, trusted=None, reason="no_match")

    score = similar.similarity_score
    settings = get_settings()

    if score < settings.rag_sim_medium:
        return RagGateDecision(
            raw=similar,
            trusted=None,
            reason="below_medium",
        )

    if similar.source_hand == "3" and score < settings.rag_sim_high:
        return RagGateDecision(
            raw=similar,
            trusted=None,
            reason="hand3_requires_high",
        )

    return RagGateDecision(raw=similar, trusted=similar, reason="trusted")
