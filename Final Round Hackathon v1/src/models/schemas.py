"""Agent input/output shapes — matches LLD artifact names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SanitizedText:
    """Guardrail output — safe for DB, embed, and LLM."""

    text: str
    blocked: bool = False
    redaction_count: int = 0


@dataclass(frozen=True)
class ClassificationResult:
    use_case_category: str
    subcategory: Optional[str] = None
    confidence_hint: str = "medium"  # low | medium | high
    source: str = "gemini"  # gemini | keyword


@dataclass(frozen=True)
class RoutingResult:
    department_queue: str
    priority: str
    sla_hours: int


@dataclass(frozen=True)
class ResolutionResult:
    steps: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    low_grounding: bool = True
    similarity_score: float = 0.0


@dataclass(frozen=True)
class SupervisorDecision:
    hand: str  # "1" | "2" | "3"
    c_total: float
    escalation_required: bool
    status: str
    policy_trigger: Optional[str] = None


@dataclass(frozen=True)
class PipelineResult:
    sanitized: SanitizedText
    classification: ClassificationResult
    routing: RoutingResult
    resolution: ResolutionResult
    decision: SupervisorDecision
