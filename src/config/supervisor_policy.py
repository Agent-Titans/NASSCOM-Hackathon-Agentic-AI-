"""
Supervisor routing policy — loaded from config/routing_rules.json.

LLD reference: #supervisor-agent, #supervisor-decision-matrix

Modes:
- strict_lld: pure c_total bands + policy_force_hand3; low_grounding → Hand 2 (team triage)
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
class SupervisorPolicy:
    """Active Supervisor decision policy for the current mode."""

    mode: str
    lld_section: str
    low_grounding_hand: str
    hand1_playbook: Hand1PlaybookPolicy
    apply_similarity_hand1_cap: bool
    force_hand3_categories: tuple[str, ...]


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
    return SupervisorPolicy(
        mode=mode,
        lld_section=str(cfg.get("lld_section", "#supervisor-agent")),
        low_grounding_hand=str(cfg.get("low_grounding_hand", "3")),
        hand1_playbook=playbook,
        apply_similarity_hand1_cap=bool(cfg.get("apply_similarity_hand1_cap", False)),
        force_hand3_categories=tuple(rules.get("policy_force_hand3_categories", [])),
    )


def matches_hand1_playbook(
    *,
    category: str,
    source_hand: Optional[str],
    similarity: float,
    low_grounding: bool,
) -> bool:
    """True when ticket matches configured Hand-1 playbook policy."""
    policy = get_supervisor_policy().hand1_playbook
    if not policy.enabled or low_grounding:
        return False
    if category not in policy.categories:
        return False
    if source_hand != policy.min_source_hand:
        return False
    return similarity >= policy.min_similarity
