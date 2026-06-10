"""Historical success rate by category — feeds Supervisor c_total (LLD)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.db.models import ClassificationArtifact, Feedback, Ticket
from src.services.process_cache import (
    get_historical_rate,
    invalidate_historical_cache,
    set_historical_rate,
)

_DEFAULT = 0.5
_MIN_SAMPLES = 3

__all__ = ["historical_success_for_category", "invalidate_historical_cache"]


def historical_success_for_category(session: Session, category: str) -> float:
    """
    Share of positive feedback for tickets in this category.

    Returns 0.5 when insufficient data (conservative default per LLD).
    """
    if not category:
        return _DEFAULT

    cached = get_historical_rate(category)
    if cached is not None:
        return cached

    rows = (
        session.query(Feedback.outcome)
        .join(Ticket, Feedback.ticket_id == Ticket.ticket_id)
        .join(
            ClassificationArtifact,
            ClassificationArtifact.ticket_id == Ticket.ticket_id,
        )
        .filter(ClassificationArtifact.use_case_category == category)
        .all()
    )
    if len(rows) < _MIN_SAMPLES:
        set_historical_rate(category, _DEFAULT)
        return _DEFAULT

    worked = sum(1 for (outcome,) in rows if outcome == "worked")
    rate = max(0.25, min(0.85, worked / len(rows)))
    set_historical_rate(category, rate)
    return rate
