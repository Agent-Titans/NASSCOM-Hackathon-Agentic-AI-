"""
Classifier agent — Gemini primary (LLD), trusted RAG second, keyword fallback last.
"""
from __future__ import annotations

from typing import Optional

from src.agents.keyword_index import score_categories
from src.clients.gemini_client import GeminiClient
from src.models.schemas import ClassificationResult, SanitizedText, SimilarTicketMatch

# Background "security policy" context must not alone justify Security category.
_SECURITY_INCIDENT_MARKERS = (
    "breach",
    "phishing",
    "malware",
    "ransomware",
    "compromised",
    "unauthorized access",
    "credential leak",
    "leaked password",
    "suspicious email",
    "secret access key",
    "api key",
    "accidentally pushed",
    "public github",
    "public repository",
    "exposed credential",
    "leaked secret",
    "purge the git",
    "git commit history",
)
_INFRA_CORE_MARKERS = (
    "docker",
    "hypervisor",
    "virtualization",
    "bios",
    "hvci",
    "virtual machine",
    "hardware-assisted",
)
_APP_CORE_MARKERS = ("compilation", "runtime error", "exception", "stack trace")

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

    def classify(
        self,
        sanitized: SanitizedText,
        similar: Optional[SimilarTicketMatch] = None,
    ) -> ClassificationResult:
        if sanitized.blocked or not sanitized.text:
            return ClassificationResult(
                use_case_category="Security",
                subcategory="policy",
                confidence_hint="low",
                source="gemini_unavailable",
            )

        parsed = self.gemini.classify_ticket(sanitized.text)
        if parsed:
            cat = parsed.get("use_case_category", "Application")
            if cat not in _VALID_CATEGORIES:
                cat = "Application"
            cat = self._finalize_category(cat, sanitized.text)
            hint = parsed.get("confidence_hint", "medium")
            if hint not in ("low", "medium", "high"):
                hint = "medium"
            return ClassificationResult(
                use_case_category=cat,
                subcategory=parsed.get("subcategory"),
                confidence_hint=hint,
                source="gemini",
            )

        if similar:
            cat = self._finalize_category(
                similar.classification.use_case_category, sanitized.text
            )
            return ClassificationResult(
                use_case_category=cat,
                subcategory=similar.classification.subcategory or "similar_ticket",
                confidence_hint=similar.classification.confidence_hint,
                source="rag",
            )

        return self._keyword_fallback(sanitized.text)

    @staticmethod
    def _finalize_category(category: str, text: str) -> str:
        """Promote true security incidents, then strip contextual false-positives."""
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return "Security"
        return ClassifierAgent._reconcile_security_false_positive(category, text)

    @staticmethod
    def _reconcile_security_false_positive(category: str, text: str) -> str:
        """
        Post-Gemini safety net: downgrade contextual Security false-positives.

        Example: Docker/hypervisor failure mentioning 'security policy updates'
        must stay Infrastructure/Application, not Security (Hand 3 kill switch).
        """
        if category != "Security":
            return category
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return category
        if any(marker in lower for marker in _INFRA_CORE_MARKERS):
            return "Infrastructure"
        if any(marker in lower for marker in _APP_CORE_MARKERS):
            return "Application"
        return category

    @staticmethod
    def _keyword_fallback(text: str) -> ClassificationResult:
        ranked = score_categories(text)
        cat = ranked[0][0] if ranked else "Application"
        if cat not in _VALID_CATEGORIES:
            cat = "Application"
        score = ranked[0][1] if ranked else 0.0
        cat = ClassifierAgent._finalize_category(cat, text)
        hint = "high" if cat == "Security" else ("medium" if score >= 0.5 else "low")
        return ClassificationResult(
            use_case_category=cat,
            subcategory="keyword",
            confidence_hint=hint,
            source="keyword",
        )
