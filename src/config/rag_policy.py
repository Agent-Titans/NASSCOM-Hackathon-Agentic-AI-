"""RAG similarity bands — raw scores only, no boosting."""
from __future__ import annotations

from src.config.settings import get_settings


def confidence_hint_from_similarity(score: float) -> str:
    """Map raw retrieval score to classifier confidence."""
    s = get_settings()
    if score >= s.rag_sim_high:
        return "high"
    if score >= s.rag_sim_medium:
        return "medium"
    return "low"


def is_low_grounding_similarity(score: float) -> bool:
    """Weak retrieval — Supervisor should not treat as Hand 1."""
    return score < get_settings().rag_sim_medium


def blocks_hand1_similarity(score: float) -> bool:
    """Medium confidence RAG — cap at Hand 2."""
    return score < get_settings().rag_sim_high


def is_trusted_rag_match(score: float) -> bool:
    """Only trust RAG category/steps when similarity is at least medium."""
    return score >= get_settings().rag_sim_medium
