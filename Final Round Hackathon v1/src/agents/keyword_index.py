"""
Keyword index for classifier fallback.

Data structure: inverted index — token -> list of (category, weight).
Lookup per ticket: O(t * d) where t = tokens, d = avg categories per token (small).

Build once at startup: O(total keywords).
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Tuple

# Use Case 1 categories (LLD) -> representative keywords
_CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Infrastructure": ["server", "hardware", "printer", "laptop", "datacenter", "outage"],
    "Application": ["software", "app", "crash", "bug", "install", "update"],
    "Security": [
        "breach",
        "vpn",
        "malware",
        "phishing",
        "security",
        "hack",
        "incident",
        "unauthorized",
        "escalat",
        "ransomware",
        "exfiltration",
    ],
    "Database": ["database", "sql", "query", "deadlock", "oracle", "postgres"],
    "Storage": ["storage", "disk", "backup", "sharepoint", "file"],
    "Network": ["network", "wifi", "dns", "latency", "firewall", "connection"],
    "Access Management": ["password", "login", "mfa", "access", "account", "permissions", "sso"],
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    """Split text into lowercase tokens — O(n)."""
    return _TOKEN_RE.findall(text.lower())


def build_inverted_index() -> Dict[str, List[Tuple[str, int]]]:
    """
    Map each keyword token to categories that care about it.
    Duplicate tokens in same category only stored once.
    """
    index: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
    for category, words in _CATEGORY_KEYWORDS.items():
        seen = set()
        for w in words:
            if w in seen:
                continue
            seen.add(w)
            index[w].append((category, 1))
    return dict(index)


# Module-level singleton — built once (O(1) per process after import).
INVERTED_INDEX = build_inverted_index()


def score_categories(text: str) -> List[Tuple[str, float]]:
    """
    Score each category by token hits — O(t * d).
    Returns sorted list (best first) using counting sort style bucket by score.
    """
    tokens = _tokenize(text)
    if not tokens:
        return []

    scores: Dict[str, int] = defaultdict(int)
    for token in tokens:
        for category, weight in INVERTED_INDEX.get(token, ()):
            scores[category] += weight

    if not scores:
        return [("Application", 0.0)]

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    max_score = ranked[0][1] or 1
    return [(cat, hit / max_score) for cat, hit in ranked]
