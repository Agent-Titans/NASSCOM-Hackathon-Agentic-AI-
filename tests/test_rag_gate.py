"""RAG trust gate — weak matches must not drive routing."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.schemas import ClassificationResult, ResolutionResult, SimilarTicketMatch
from src.services.rag_gate import evaluate_rag_match


def _match(score: float, hand: str | None = "2") -> SimilarTicketMatch:
    return SimilarTicketMatch(
        ticket_id="rag-demo",
        title="demo",
        similarity_score=score,
        classification=ClassificationResult("Application", source="rag"),
        resolution=ResolutionResult(steps=["s"], low_grounding=False),
        department_queue="Software",
        source_hand=hand,
    )


def test_no_match():
    d = evaluate_rag_match(None)
    assert d.trusted is None
    assert d.reason == "no_match"


def test_below_medium_rejected():
    d = evaluate_rag_match(_match(0.47, "3"))
    assert d.raw is not None
    assert d.trusted is None
    assert d.reason == "below_medium"


def test_hand3_requires_high_similarity():
    d = evaluate_rag_match(_match(0.62, "3"))
    assert d.trusted is None
    assert d.reason == "hand3_requires_high"


def test_hand3_trusted_when_high():
    d = evaluate_rag_match(_match(0.75, "3"))
    assert d.trusted is not None
    assert d.reason == "trusted"


def test_hand2_medium_trusted():
    d = evaluate_rag_match(_match(0.60, "2"))
    assert d.trusted is not None
    assert d.reason == "trusted"
