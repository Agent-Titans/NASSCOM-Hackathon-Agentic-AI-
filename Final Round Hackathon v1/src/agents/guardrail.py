"""
Guardrail agent — redact PII/secrets before any other step.

Time: O(n * p) where n = text length, p = number of compiled patterns (small constant).
Space: O(n) for output string.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from src.models.schemas import SanitizedText

# Compiled once at import — avoids re-compiling per ticket (amortized O(1) setup).
_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"), "[SECRET_REDACTED]"),
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "[ID_REDACTED]"),
]

# Simple injection phrases — linear scan over fixed list (O(n * k), k tiny).
_INJECTION_MARKERS = (
    "ignore previous instructions",
    "system prompt",
    "you are now",
)


@dataclass
class GuardrailAgent:
    """Rule-based sanitizer — no LLM."""

    def apply_guardrails(self, raw_text: str) -> SanitizedText:
        if not raw_text or not raw_text.strip():
            return SanitizedText(text="", blocked=True, redaction_count=0)

        lowered = raw_text.lower()
        for marker in _INJECTION_MARKERS:
            if marker in lowered:
                # Policy: unsafe instruction-like content → block for manual review.
                return SanitizedText(text="", blocked=True, redaction_count=0)

        text = raw_text
        redactions = 0
        for pattern, replacement in _PATTERNS:
            text, count = pattern.subn(replacement, text)
            redactions += count

        return SanitizedText(text=text.strip(), blocked=False, redaction_count=redactions)
