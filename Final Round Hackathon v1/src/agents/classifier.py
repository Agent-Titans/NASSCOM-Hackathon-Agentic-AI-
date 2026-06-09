"""
Classifier agent — Gemini first, keyword inverted-index fallback.

Fallback scoring: O(t * d) via keyword_index (no extra LLM cost).
"""
from __future__ import annotations

from src.agents.keyword_index import score_categories
from src.clients.gemini_client import GeminiClient
from src.models.schemas import ClassificationResult, SanitizedText

_VALID_CATEGORIES = frozenset(
    {
        "Infrastructure",
        "Application",
        "Security",
        "Database",
        "Storage",
        "Network",
        "Access Management",
    }
)


class ClassifierAgent:
    def __init__(self, gemini: GeminiClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()

    def classify(self, sanitized: SanitizedText) -> ClassificationResult:
        if sanitized.blocked or not sanitized.text:
            return ClassificationResult(
                use_case_category="Security",
                subcategory="policy",
                confidence_hint="low",
                source="keyword",
            )

        parsed = self.gemini.classify_ticket(sanitized.text)
        if parsed:
            cat = parsed.get("use_case_category", "Application")
            if cat not in _VALID_CATEGORIES:
                cat = "Application"
            hint = parsed.get("confidence_hint", "medium")
            if hint not in ("low", "medium", "high"):
                hint = "medium"
            return ClassificationResult(
                use_case_category=cat,
                subcategory=parsed.get("subcategory"),
                confidence_hint=hint,
                source="gemini",
            )

        return self._keyword_fallback(sanitized.text)

    def _keyword_fallback(self, text: str) -> ClassificationResult:
        """Inverted-index vote — O(t * d)."""
        ranked = score_categories(text)
        best_cat, score = ranked[0]
        hint = "high" if score >= 0.8 else "medium" if score >= 0.4 else "low"
        return ClassificationResult(
            use_case_category=best_cat,
            subcategory="keyword_match",
            confidence_hint=hint,
            source="keyword",
        )
