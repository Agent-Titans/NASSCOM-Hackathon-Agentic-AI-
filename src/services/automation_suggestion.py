"""
Append an automation hint when resolution closely matches a prior incident.

Runs after Resolver; O(n) over resolution steps where n is small (typically < 10).
Skips Security category and low-similarity matches per supervisor_policy.json.
"""
from __future__ import annotations

from dataclasses import replace

from src.config.supervisor_policy import get_supervisor_policy
from src.models.schemas import ClassificationResult, ResolutionResult

_AUTOMATION_PREFIX = "Automation opportunity:"


def maybe_append_automation_suggestion(
    resolution: ResolutionResult,
    classification: ClassificationResult,
) -> ResolutionResult:
    """Add a repeat-pattern automation hint to resolution steps when policy allows."""
    policy = get_supervisor_policy().automation_suggestion
    if not policy.enabled or resolution.low_grounding:
        return resolution
    if resolution.similarity_score < policy.min_similarity:
        return resolution
    if classification.use_case_category == "Security":
        return resolution

    ref = resolution.matched_ticket_id or "prior incident"
    pct = f"{resolution.similarity_score:.0%}"
    note = (
        f"{_AUTOMATION_PREFIX} This {classification.use_case_category} pattern closely "
        f"matches a prior incident ({ref}, {pct} similarity). Consider a runbook or "
        "self-service workflow to reduce repeat tickets."
    )
    steps = list(resolution.steps_requester or resolution.steps)
    if any(s.startswith(_AUTOMATION_PREFIX) for s in steps):
        return resolution
    steps.append(note)
    kwargs: dict = {"steps": steps}
    if resolution.steps_requester is not None:
        kwargs["steps_requester"] = steps
    if resolution.steps_assignee is not None:
        assignee = list(resolution.steps_assignee)
        if not any(s.startswith(_AUTOMATION_PREFIX) for s in assignee):
            assignee.append(note)
        kwargs["steps_assignee"] = assignee
    return replace(resolution, **kwargs)
