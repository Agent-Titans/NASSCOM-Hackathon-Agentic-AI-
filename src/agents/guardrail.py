"""
Guardrail AI agent — dual-layer defense against prompt injection (LLD § Guardrail).

Layer 1: Local regex (no API cost) — blocks obvious override phrases.
Layer 2: Gemini defensive scan — treats ticket body as untrusted static data.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

from src.agents.guardrail_exceptions import SecurityGuardrailException
from src.clients.gemini_client import GeminiClient, SECURITY_FAIL_TOKEN
from src.models.schemas import SanitizedText

# ---------------------------------------------------------------------------
# PII / secrets — redact before any embedding, retrieval, or downstream LLM.
# ---------------------------------------------------------------------------
_PII_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"), "[SECRET_REDACTED]"),
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "[ID_REDACTED]"),
]

# ---------------------------------------------------------------------------
# Layer 1 — fast regex pre-check (runs BEFORE any Gemini API call).
# Catches system-override / instruction-hijack language in ticket text.
# ---------------------------------------------------------------------------
# Obvious employee support requests — skip flaky Layer 2 when Layer 1 is clean.
_BENIGN_IT_MARKERS: Tuple[str, ...] = (
    "vpn",
    "error",
    "whitelist",
    "white list",
    "firewall",
    "cannot connect",
    "wifi",
    "password",
    "printer",
    "outlook",
    "teams",
    "chrome",
    "not working",
    "unable to",
    "need help",
    "locked out",
)

_INJECTION_REGEXES: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?prior\s+instructions",
        r"system\s+administrator\s+override",
        r"administrator\s+override",
        r"override\s+initiated",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"you\s+must\s+immediately\s+classify",
        r"do\s+not\s+run\s+the\s+resolver",
        r"skip\s+the\s+(classifier|resolver|supervisor)",
        r"classify\s+this\s+ticket\s+as\s+['\"]?\w+['\"]?\s*,?\s*set\s+confidence",
        r"output\s+(a\s+)?response\s+that\s+says",
        r"<\s*/?\s*system\s*>",
        r"jailbreak",
        r"developer\s+mode\s+enabled",
    )
)


@dataclass
class GuardrailAI:
    """
    LLD Guardrail agent — sanitize PII and block prompt-injection attempts.

    On security failure raises SecurityGuardrailException (never returns
    blocked=True for injection; orchestrator uses exception for hard stop).
    """

    gemini: GeminiClient = field(default_factory=GeminiClient)

    def apply_guardrails(self, raw_text: str) -> SanitizedText:
        """
        Run dual-layer guardrail. Returns sanitized text on success.

        Raises:
            SecurityGuardrailException: Layer 1 regex or Layer 2 LLM scan failure.
        """
        if not raw_text or not raw_text.strip():
            raise SecurityGuardrailException("empty_ticket", layer="regex")

        # ----- Layer 1: regex pre-check (zero API tokens) -----
        self._layer1_regex_scan(raw_text)

        # Redact PII/secrets before Layer 2 and before downstream agents.
        text, redactions = self._redact_pii(raw_text)

        # ----- Layer 2: defensive Gemini scan on redacted static text -----
        self._layer2_llm_scan(text)

        return SanitizedText(text=text.strip(), blocked=False, redaction_count=redactions)

    @staticmethod
    def _is_benign_it_request(text: str) -> bool:
        """True for routine helpdesk text that should not depend on Layer 2 availability."""
        lower = text.lower()
        return any(marker in lower for marker in _BENIGN_IT_MARKERS)

    @staticmethod
    def _layer1_regex_scan(raw_text: str) -> None:
        """
        Layer 1 — local regex only.

        If any override / instruction-hijack pattern matches, abort immediately.
        This prevents wasted Classifier/Resolver Gemini calls on known attacks.
        """
        for pattern in _INJECTION_REGEXES:
            if pattern.search(raw_text):
                raise SecurityGuardrailException(
                    f"regex_injection:{pattern.pattern[:48]}",
                    layer="regex",
                )

    def _layer2_llm_scan(self, redacted_text: str) -> None:
        """
        Layer 2 — Gemini defensive guardrail.

        The model must treat `redacted_text` as untrusted user data, not commands.
        Returns SECURITY_FAIL token when an override attempt is detected.

        Fail-open on API/inconclusive errors so legitimate tickets still route when
        Gemini is unavailable (Layer 1 regex remains fail-closed).
        """
        if GuardrailAI._is_benign_it_request(redacted_text):
            return

        verdict = self.gemini.scan_prompt_injection(redacted_text)
        if verdict == SECURITY_FAIL_TOKEN:
            raise SecurityGuardrailException("llm_injection_detected", layer="llm")

    @staticmethod
    def _redact_pii(raw_text: str) -> Tuple[str, int]:
        """PII/secrets scrub per LLD before downstream embedding or LLM prompts."""
        text = raw_text
        redactions = 0
        for pattern, replacement in _PII_PATTERNS:
            text, count = pattern.subn(replacement, text)
            redactions += count
        return text, redactions


# Backward-compatible alias used elsewhere in the codebase.
GuardrailAgent = GuardrailAI
