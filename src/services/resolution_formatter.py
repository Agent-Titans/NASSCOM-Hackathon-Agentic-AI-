"""Post-Supervisor audience rewrite — one Gemini call for requester + assignee steps."""
from __future__ import annotations

import time
from dataclasses import replace
from typing import Optional

from src.clients.gemini_client import GeminiClient
from src.config.settings import get_settings
from src.services.resolution_steps_codec import is_schema_junk_steps
from src.models.schemas import (
    ClassificationResult,
    ResolutionResult,
    RoutingResult,
    SanitizedText,
    SimilarTicketMatch,
    SupervisorDecision,
)


class ResolutionFormatter:
    def __init__(self, gemini: GeminiClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()

    def maybe_rewrite(
        self,
        *,
        sanitized: SanitizedText,
        classification: ClassificationResult,
        routing: RoutingResult,
        resolution: ResolutionResult,
        decision: SupervisorDecision,
        trusted_similar: Optional[SimilarTicketMatch],
        pipeline_started_at: float,
    ) -> ResolutionResult:
        settings = get_settings()
        if not settings.resolution_rewrite_enabled:
            return resolution
        if decision.hand not in ("1", "2"):
            return resolution
        if classification.use_case_category == "Security":
            return resolution
        if resolution.low_grounding or not resolution.steps:
            return resolution
        if trusted_similar is None:
            return resolution

        elapsed = time.perf_counter() - pipeline_started_at
        if elapsed > settings.resolution_rewrite_skip_after_sec:
            return resolution

        formatted = self.gemini.format_resolution_audiences(
            ticket_text=sanitized.text,
            category=classification.use_case_category,
            department=routing.department_queue,
            hand=decision.hand,
            playbook_steps=resolution.steps,
            citations=resolution.citations,
            timeout=settings.resolution_rewrite_timeout_sec,
        )
        if not formatted:
            return resolution

        req = formatted.get("steps_requester") or resolution.steps
        asn = formatted.get("steps_assignee") or resolution.steps
        if is_schema_junk_steps(req) and is_schema_junk_steps(asn):
            return resolution
        if is_schema_junk_steps(req):
            req = resolution.steps
        if is_schema_junk_steps(asn):
            asn = resolution.steps
        return replace(
            resolution,
            steps=req,
            steps_requester=req,
            steps_assignee=asn,
        )
