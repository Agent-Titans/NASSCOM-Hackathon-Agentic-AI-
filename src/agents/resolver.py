"""
Resolver agent — RAG similar ticket first, then Gemini generation.

LLD: Chroma retrieval → grounded steps; weak miss → Gemini; no keyword category fallback.
"""
from __future__ import annotations

from typing import List, Optional

from src.clients.gemini_client import GeminiClient
from src.config.rag_policy import is_low_grounding_similarity
from src.services.rag_relevance import topic_buckets
from src.models.schemas import (
    ClassificationResult,
    ResolutionResult,
    RoutingResult,
    SanitizedText,
    SimilarTicketMatch,
)


class ResolverAgent:
    def __init__(self, gemini: GeminiClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()

    def resolve(
        self,
        sanitized: SanitizedText,
        classification: ClassificationResult,
        routing: RoutingResult,
        similar: Optional[SimilarTicketMatch] = None,
    ) -> ResolutionResult:
        if sanitized.blocked or not sanitized.text:
            return ResolutionResult(low_grounding=True, similarity_score=0.0)

        if similar:
            raw_score = similar.similarity_score
            return ResolutionResult(
                steps=list(similar.resolution.steps),
                citations=list(similar.resolution.citations),
                low_grounding=is_low_grounding_similarity(raw_score),
                similarity_score=raw_score,
                matched_ticket_id=similar.ticket_id,
                matched_source_hand=similar.resolution.matched_source_hand,
            )

        generated = self.gemini.generate_resolution(
            sanitized.text,
            classification.use_case_category,
            routing.department_queue,
        )
        if generated:
            steps = generated.get("steps") or []
            cites = generated.get("citations") or []
            if steps:
                # No RAG match — steps are suggestions only; do not inflate similarity.
                return ResolutionResult(
                    steps=[str(s) for s in steps],
                    citations=[str(c) for c in cites],
                    low_grounding=True,
                    similarity_score=0.35,
                )

        hardware_steps = self._hardware_steps(sanitized.text)
        if hardware_steps:
            return ResolutionResult(
                steps=hardware_steps,
                citations=[],
                low_grounding=True,
                similarity_score=0.35,
            )

        return ResolutionResult(
            steps=self._generic_steps(classification, routing),
            citations=[],
            low_grounding=True,
            similarity_score=0.35,
        )

    @staticmethod
    def _hardware_steps(text: str) -> Optional[List[str]]:
        if "hardware" not in topic_buckets(text):
            return None
        lower = text.lower()
        if any(
            marker in lower
            for marker in ("charger", "power adapter", "power cable", "battery", "charging")
        ):
            return [
                "Confirm the charger is firmly connected at the laptop and wall outlet.",
                "If available, try a known-good power adapter with the same wattage rating.",
                "Note your asset tag and charger model for the Hardware team.",
                "Hardware will arrange a replacement or depot swap per asset policy.",
            ]
        return [
            "Note your asset tag and a brief description of the hardware symptom.",
            "The Hardware team will diagnose and arrange repair or replacement.",
            "Add photos or error messages in a comment if available.",
        ]

    @staticmethod
    def _generic_steps(
        classification: ClassificationResult,
        routing: RoutingResult,
    ) -> List[str]:
        return [
            f"Your request was classified as **{classification.use_case_category}**.",
            f"The **{routing.department_queue}** team will use internal runbooks.",
            "Add screenshots or error codes in a comment to speed resolution.",
        ]
