"""
Supervisor routing policy — loaded from config/routing_rules.json.

LLD reference: #supervisor-agent, #supervisor-decision-matrix

Modes:
- strict_lld: c_total bands + policy_force_hand3; low_grounding → Hand 2; trusted H1 playbook → Hand 1
- demo: tunable policies for hackathon accuracy (hand1_playbook, low_grounding → Hand 2)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from src.config.settings import get_settings


@dataclass(frozen=True)
class Hand1PlaybookPolicy:
    enabled: bool
    categories: tuple[str, ...]
    min_source_hand: str
    min_similarity: float


@dataclass(frozen=True)
class AutomationSuggestionPolicy:
    enabled: bool
    min_similarity: float


@dataclass(frozen=True)
class SupervisorPolicy:
    """Active Supervisor decision policy for the current mode."""

    mode: str
    lld_section: str
    low_grounding_hand: str
    hand1_playbook: Hand1PlaybookPolicy
    automation_suggestion: AutomationSuggestionPolicy
    apply_similarity_hand1_cap: bool
    force_hand3_categories: tuple[str, ...]
    urgency_min_hand: dict[str, str]


def _load_rules(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_supervisor_policy() -> SupervisorPolicy:
    settings = get_settings()
    rules = _load_rules(settings.routing_rules_path)
    mode = settings.supervisor_mode
    modes = rules.get("supervisor_policy", {}).get("modes", {})
    if mode not in modes:
        raise ValueError(
            f"Unknown supervisor_mode={mode!r}; expected one of {list(modes)}"
        )
    cfg = modes[mode]
    playbook_raw = cfg.get("policy_hand1_playbook", {})
    playbook = Hand1PlaybookPolicy(
        enabled=bool(playbook_raw.get("enabled", False)),
        categories=tuple(playbook_raw.get("categories", [])),
        min_source_hand=str(playbook_raw.get("min_source_hand", "1")),
        min_similarity=float(playbook_raw.get("min_similarity", 0.55)),
    )
    automation_raw = cfg.get("policy_automation_suggestion", {})
    automation = AutomationSuggestionPolicy(
        enabled=bool(automation_raw.get("enabled", False)),
        min_similarity=float(automation_raw.get("min_similarity", 0.82)),
    )
    urgency_raw = cfg.get("urgency_min_hand", {})
    urgency_min_hand = {
        str(k).lower(): str(v)
        for k, v in urgency_raw.items()
        if str(v) in ("1", "2", "3")
    }
    if not urgency_min_hand:
        urgency_min_hand = {"low": "1", "medium": "1", "high": "2"}

    return SupervisorPolicy(
        mode=mode,
        lld_section=str(cfg.get("lld_section", "#supervisor-agent")),
        low_grounding_hand=str(cfg.get("low_grounding_hand", "3")),
        hand1_playbook=playbook,
        automation_suggestion=automation,
        apply_similarity_hand1_cap=bool(cfg.get("apply_similarity_hand1_cap", False)),
        force_hand3_categories=tuple(rules.get("policy_force_hand3_categories", [])),
        urgency_min_hand=urgency_min_hand,
    )


def min_hand_for_urgency(urgency: str | None) -> str:
    """Minimum Hand tier for ticket urgency (1 < 2 < 3)."""
    policy = get_supervisor_policy()
    key = (urgency or "medium").strip().lower()
    return policy.urgency_min_hand.get(key, policy.urgency_min_hand.get("medium", "1"))


def matches_hand1_playbook(
    *,
    category: str,
    source_hand: Optional[str],
    similarity: float,
    low_grounding: bool,
) -> bool:
    """True when trusted H1 RAG playbook match meets configured policy."""
    policy = get_supervisor_policy().hand1_playbook
    if not policy.enabled or low_grounding:
        return False
    if category not in policy.categories:
        return False
    if source_hand != policy.min_source_hand:
        return False
    return similarity >= policy.min_similarity
