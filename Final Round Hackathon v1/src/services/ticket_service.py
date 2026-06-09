"""
TicketService — single entry point for the five-agent pipeline (LLD).

Pipeline order is fixed; total local CPU work is linear in ticket text size.
"""
from __future__ import annotations

import time
from typing import Callable, TypeVar

from sqlalchemy.orm import Session

from src.agents.classifier import ClassifierAgent
from src.agents.guardrail import GuardrailAgent
from src.agents.resolver import ResolverAgent
from src.agents.router import RouterAgent
from src.agents.supervisor import SupervisorAgent
from src.db.models import Ticket, User
from src.models.schemas import (
    ClassificationResult,
    PipelineResult,
    SupervisorDecision,
)
from src.services.notification_service import NotificationService
from src.stores.artifact_store import ArtifactStore
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore

T = TypeVar("T")


class TicketService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.tickets = TicketStore(session)
        self.audit = AuditLogStore(session)
        self.artifacts = ArtifactStore(session)
        self.guardrail = GuardrailAgent()
        self.classifier = ClassifierAgent()
        self.router = RouterAgent()
        self.resolver = ResolverAgent()
        self.supervisor = SupervisorAgent()
        self.notifications = NotificationService()

    def _timed(self, ticket: Ticket, agent: str, fn: Callable[[], T]) -> T:
        """Run step and record duration in audit — O(1) log write."""
        start = time.perf_counter()
        self.audit.record(ticket, "agent_started", agent=agent)
        try:
            out = fn()
            ms = int((time.perf_counter() - start) * 1000)
            self.audit.record(
                ticket, "agent_completed", agent=agent, duration_ms=ms
            )
            return out
        except Exception as exc:
            ms = int((time.perf_counter() - start) * 1000)
            self.audit.record(
                ticket,
                "agent_failed",
                agent=agent,
                details=str(exc)[:200],
                duration_ms=ms,
            )
            raise

    def process_ticket(self, ticket: Ticket) -> PipelineResult:
        """
        Run Guardrail → Classifier → Router → Resolver → Supervisor.
        Persists artifacts and final Hand on ticket.
        """
        self.audit.record(ticket, "pipeline_started")

        sanitized = self._timed(
            ticket, "guardrail", lambda: self.guardrail.apply_guardrails(ticket.description_raw)
        )

        if sanitized.blocked:
            # Fast path — O(1) policy without calling Gemini.
            blocked_class = ClassificationResult(
                "Security", confidence_hint="low", source="keyword"
            )
            blocked_route = self.router.route(blocked_class, ticket.urgency)
            blocked_resolution = self.resolver.resolve(
                sanitized, blocked_class, blocked_route
            )
            decision = SupervisorDecision(
                hand="3",
                c_total=0.0,
                escalation_required=True,
                status="ESCALATED",
                policy_trigger="guardrail_block",
            )
            self._finalize(
                ticket,
                sanitized,
                blocked_class,
                blocked_route,
                blocked_resolution,
                decision,
            )
            self.audit.record(ticket, "pipeline_completed", details="hand=3 guardrail")
            return PipelineResult(
                sanitized=sanitized,
                classification=blocked_class,
                routing=blocked_route,
                resolution=blocked_resolution,
                decision=decision,
            )

        classification = self._timed(
            ticket,
            "classifier",
            lambda: self.classifier.classify(sanitized),
        )
        routing = self._timed(
            ticket,
            "router",
            lambda: self.router.route(classification, ticket.urgency),
        )
        resolution = self._timed(
            ticket,
            "resolver",
            lambda: self.resolver.resolve(sanitized, classification, routing),
        )
        sentiment = self.supervisor.sentiment_from_classification(classification)
        # Playbook hits get a small historical boost — O(1) check.
        historical = 0.65 if not resolution.low_grounding else 0.5
        decision = self._timed(
            ticket,
            "supervisor",
            lambda: self.supervisor.decide(
                classification,
                resolution,
                sentiment=sentiment,
                historical_success=historical,
            ),
        )

        self._finalize(
            ticket, sanitized, classification, routing, resolution, decision
        )
        self.audit.record(
            ticket,
            "pipeline_completed",
            details=f"hand={decision.hand} c_total={decision.c_total:.2f}",
        )

        user = self.session.get(User, ticket.user_id)
        requester_email = user.email if user else "unknown"
        self.notifications.send_hand_message(
            ticket.ticket_id, decision, requester_email
        )

        return PipelineResult(
            sanitized=sanitized,
            classification=classification,
            routing=routing,
            resolution=resolution,
            decision=decision,
        )

    def _finalize(
        self,
        ticket: Ticket,
        sanitized,
        classification,
        routing,
        resolution,
        decision,
    ) -> None:
        self.tickets.update_hand(
            ticket,
            hand=decision.hand,
            confidence=decision.c_total,
            status=decision.status,
            department_queue=routing.department_queue if routing else "SecOps",
            priority=routing.priority if routing else "P1",
            sla_hours=routing.sla_hours if routing else 4,
            escalation_required=decision.escalation_required,
            sanitized=sanitized.text if sanitized else None,
        )
        if classification:
            self.artifacts.save_classification(ticket, classification)
        if resolution:
            self.artifacts.save_resolution(ticket, resolution)
