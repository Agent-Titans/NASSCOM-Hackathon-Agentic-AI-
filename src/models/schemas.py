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
    source: str = "gemini"  # gemini | rag | gemini_unavailable


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
    matched_ticket_id: Optional[str] = None
    matched_source_hand: Optional[str] = None  # corpus hand "1"|"2"|"3" when from RAG
    steps_requester: Optional[List[str]] = None  # friendly self-help (Hand 1/2 UI)
    steps_assignee: Optional[List[str]] = None  # technical card for agent portal


@dataclass(frozen=True)
class SimilarTicketMatch:
    """Prior ticket hit from ChromaDB / keyword retrieval."""

    ticket_id: str
    title: str
    similarity_score: float
    classification: ClassificationResult
    resolution: ResolutionResult
    department_queue: str
    source: str = "chroma"  # chroma | keyword_db
    source_hand: Optional[str] = None  # demo corpus / ticket hand when known


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
    decision: SupervisorDecision
    classification: Optional[ClassificationResult] = None
    routing: Optional[RoutingResult] = None
    resolution: Optional[ResolutionResult] = None
