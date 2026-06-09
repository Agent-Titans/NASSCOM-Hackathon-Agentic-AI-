"""
Thin Gemini HTTP client — classify + generate only when API key present.

Network calls dominate latency; local work stays O(1) or O(n) on small JSON.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.google_api_key.strip())

    def _post(self, model: str, body: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        key = self.settings.google_api_key
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={key}"
        )
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())

    def classify_ticket(self, sanitized_text: str) -> Optional[Dict[str, Any]]:
        """Return parsed JSON or None on failure."""
        if not self.available:
            return None
        prompt = (
            "Classify this IT support ticket. Reply ONLY with JSON:\n"
            '{"use_case_category":"...", "subcategory":"...", "confidence_hint":"low|medium|high"}\n'
            "Categories: Infrastructure, Application, Security, Database, Storage, Network, Access Management.\n"
            f"Ticket:\n{sanitized_text[:4000]}"
        )
        try:
            raw = self._post(
                self.settings.gemini_model_classify,
                {"contents": [{"parts": [{"text": prompt}]}]},
            )
            text = (
                raw.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            start, end = text.find("{"), text.rfind("}") + 1
            if start < 0 or end <= start:
                return None
            return json.loads(text[start:end])
        except (urllib.error.HTTPError, json.JSONDecodeError, KeyError, IndexError) as exc:
            logger.warning("Gemini classify failed: %s", exc)
            return None
