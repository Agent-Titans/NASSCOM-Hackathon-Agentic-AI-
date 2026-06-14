"""
TicketService — orchestrates the five-step incident pipeline.

Fixed order: Guardrail → Retrieval → Classifier → Router → Resolver → Supervisor.
Each step writes to the audit log; total work is linear in ticket text length.
"""
from __future__ import annotations

import time
from dataclasses import replace
from typing import Callable, Optional, TypeVar

from sqlalchemy.orm import Session

from src.agents.classifier import ClassifierAgent
from src.agents.guardrail import GuardrailAI
from src.agents.guardrail_exceptions import SecurityGuardrailException
from src.agents.resolver import ResolverAgent
from src.agents.router import RouterAgent
from src.agents.supervisor import SupervisorAgent
from src.db.models import AgentRun, Ticket, User
from src.models.schemas import (
    ClassificationResult,
    PipelineResult,
    ResolutionResult,
    RoutingResult,
    SanitizedText,
    SupervisorDecision,
)
from src.services.automation_suggestion import maybe_append_automation_suggestion
from src.services.historical_success_service import historical_success_for_category
from src.services.notification_service import NotificationService
from src.services.rag_gate import evaluate_rag_match
from src.services.resolution_formatter import ResolutionFormatter
from src.services.ticket_retrieval import TicketRetrievalService
from src.stores.agent_run_store import AgentRunStore
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
        self.agent_runs = AgentRunStore(session)
        self.guardrail = GuardrailAI()
        self.classifier = ClassifierAgent()
        self.router = RouterAgent()
        self.resolver = ResolverAgent()
        self.supervisor = SupervisorAgent()
        self.notifications = NotificationService()
        self.retrieval = TicketRetrievalService()
        self.resolution_formatter = ResolutionFormatter()

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

        SECURITY: If guardrail raises SecurityGuardrailException, the pipeline
        stops immediately — Classifier, Router, and Resolver are NOT invoked.
        Ticket is force-routed to Hand 3 with guardrail_ok=False on AgentRun.
        """
        from src.services.retrieval_bootstrap import start_retrieval_warm_background

        start_retrieval_warm_background(api_embeds=True, delay_seconds=0)
        self.audit.record(ticket, "pipeline_started")
        pipeline_started_at = time.perf_counter()
        agent_run = self.agent_runs.begin(ticket)

        # ------------------------------------------------------------------
        # GUARDRAIL — PII redaction and injection scan before retrieval/classify
        # ------------------------------------------------------------------
        try:
            sanitized = self._run_guardrail(ticket, agent_run)
        except SecurityGuardrailException as exc:
            # Hard stop: classifier, router, and resolver are not invoked.
            return self._security_halt(ticket, agent_run, exc)

        retrieval_text = f"{ticket.title}\n{sanitized.text}".strip()
        raw_similar, retrieval_references = self._timed(
            ticket,
            "retrieval",
            lambda: self.retrieval.find_similar_and_references(
                self.session,
                retrieval_text,
                exclude_ticket_id=ticket.ticket_id,
            ),
        )
        rag_gate = evaluate_rag_match(raw_similar, query_text=retrieval_text)
        trusted_similar = rag_gate.trusted

        if rag_gate.trusted:
            self.audit.record(
                ticket,
                "rag_hit",
                agent="retrieval",
                details=(
                    f"ticket={rag_gate.raw.ticket_id[:8]} "
                    f"score={rag_gate.raw.similarity_score:.2f} "
                    f"hand={rag_gate.raw.source_hand} gate={rag_gate.reason}"
                ),
            )
        elif rag_gate.raw:
            self.audit.record(
                ticket,
                "rag_miss",
                agent="retrieval",
                details=(
                    f"ticket={rag_gate.raw.ticket_id[:8]} "
                    f"score={rag_gate.raw.similarity_score:.2f} "
                    f"gate={rag_gate.reason}"
                ),
            )
        else:
            self.audit.record(
                ticket,
                "rag_miss",
                agent="retrieval",
                details="gate=no_match",
            )

        classification = self._timed(
            ticket,
            "classifier",
            lambda: self.classifier.classify(
                sanitized, trusted_similar, title=ticket.title
            ),
        )
        self.agent_runs.mark_classification(agent_run, ok=True)
        self.audit.record(
            ticket,
            "classified",
            agent="classifier",
            details=(
                f"category={classification.use_case_category} "
                f"source={classification.source} "
                f"hint={classification.confidence_hint}"
            ),
        )

        routing = self._timed(
            ticket,
            "router",
            lambda: self.router.route(classification, ticket.urgency),
        )
        self.agent_runs.mark_routing(agent_run, ok=True)

        if classification.use_case_category == "Security":
            resolution = ResolutionResult(
                steps=[
                    "Security incident logged for specialist review.",
                    "Do not share credentials or follow unverified remediation links.",
                    "SecOps will contact you per security response SLA.",
                ],
                citations=["SEC-POLICY"],
                low_grounding=True,
                similarity_score=0.0,
            )
            self.audit.record(
                ticket,
                "security_short_circuit",
                agent="resolver",
                details="skipped_llm_resolver",
            )
            self.agent_runs.mark_resolver(agent_run, ok=True)
        else:
            resolution = self._timed(
                ticket,
                "resolver",
                lambda: self.resolver.resolve(
                    sanitized, classification, routing, trusted_similar
                ),
            )
            resolution = replace(resolution, references=retrieval_references)
            self.agent_runs.mark_resolver(agent_run, ok=True)

        sentiment = self.supervisor.sentiment_from_classification(classification)
        historical = historical_success_for_category(
            self.session, classification.use_case_category
        )
        # Bootstrap prior when category lacks feedback but RAG grounding is trusted.
        if not resolution.low_grounding and historical <= 0.5:
            historical = 0.65
        decision = self._timed(
            ticket,
            "supervisor",
            lambda: self.supervisor.decide(
                classification,
                resolution,
                sentiment=sentiment,
                historical_success=historical,
                urgency=ticket.urgency,
            ),
        )
        self.agent_runs.mark_supervisor(agent_run, ok=True)

        resolution = self._timed(
            ticket,
            "resolution_format",
            lambda: self.resolution_formatter.maybe_rewrite(
                sanitized=sanitized,
                classification=classification,
                routing=routing,
                resolution=resolution,
                decision=decision,
                trusted_similar=trusted_similar,
                pipeline_started_at=pipeline_started_at,
            ),
        )

        before_auto = len(resolution.steps)
        resolution = maybe_append_automation_suggestion(resolution, classification)
        if len(resolution.steps) > before_auto:
            self.audit.record(
                ticket,
                "automation_suggestion",
                agent="supervisor",
                details=(
                    f"similarity={resolution.similarity_score:.2f} "
                    f"match={resolution.matched_ticket_id or 'none'}"
                ),
            )

        self._finalize(
            ticket, sanitized, classification, routing, resolution, decision
        )
        trigger = decision.policy_trigger or "c_total_band"
        self.audit.record(
            ticket,
            "pipeline_completed",
            details=(
                f"hand={decision.hand} c_total={decision.c_total:.2f} "
                f"policy={trigger} classifier={classification.source}"
            ),
        )

        user = self.session.get(User, ticket.user_id)
        requester_email = user.email if user else "unknown"
        self.notifications.send_hand_message(
            ticket.ticket_id, decision, requester_email
        )
        self.notifications.notify_ticket_opened(self.session, ticket)

        return PipelineResult(
            sanitized=sanitized,
            classification=classification,
            routing=routing,
            resolution=resolution,
            decision=decision,
        )

    def _run_guardrail(self, ticket: Ticket, agent_run: AgentRun) -> SanitizedText:
        """
        Execute GuardrailAI.apply_guardrails() and persist guardrail_ok=True.

        Separated so SecurityGuardrailException can be caught at orchestrator
        level without being swallowed by generic _timed error handling.
        """
        start = time.perf_counter()
        self.audit.record(ticket, "agent_started", agent="guardrail")
        try:
            sanitized = self.guardrail.apply_guardrails(ticket.description_raw)
            ms = int((time.perf_counter() - start) * 1000)
            self.audit.record(
                ticket, "agent_completed", agent="guardrail", duration_ms=ms
            )
            self.agent_runs.mark_guardrail(agent_run, ok=True)
            return sanitized
        except SecurityGuardrailException:
            ms = int((time.perf_counter() - start) * 1000)
            self.audit.record(
                ticket,
                "agent_failed",
                agent="guardrail",
                details="SecurityGuardrailException",
                duration_ms=ms,
            )
            self.agent_runs.mark_guardrail(agent_run, ok=False)
            raise

    def _security_halt(
        self,
        ticket: Ticket,
        agent_run: AgentRun,
        exc: SecurityGuardrailException,
    ) -> PipelineResult:
        """
        Pipeline failure state for injection / override attempts.

        - Stops before Classifier, Router, Resolver (already stopped by caller).
        - Forces Hand 3 / HUMAN_REVIEW.
        - AgentRun.guardrail_ok remains False; downstream *_ok flags stay False.
        """
        decision = SupervisorDecision(
            hand="3",
            c_total=0.0,
            escalation_required=True,
            status="HUMAN_REVIEW",
            policy_trigger=f"guardrail_{exc.layer}",
        )
        empty_sanitized = SanitizedText(text="", blocked=True, redaction_count=0)

        self.tickets.update_hand(
            ticket,
            hand=decision.hand,
            confidence=0.0,
            status=decision.status,
            department_queue="SecOps",
            priority="P0",
            sla_hours=4,
            escalation_required=True,
            sanitized=None,
        )

        self.audit.record(
            ticket,
            "security_halt",
            agent="guardrail",
            details=f"layer={exc.layer} reason={exc.reason}",
        )
        self.audit.record(
            ticket,
            "pipeline_completed",
            details=f"hand=3 guardrail_fail layer={exc.layer}",
        )

        user = self.session.get(User, ticket.user_id)
        if user:
            self.notifications.send_hand_message(
                ticket.ticket_id, decision, user.email
            )
            self.notifications.notify_ticket_opened(self.session, ticket)

        return PipelineResult(
            sanitized=empty_sanitized,
            classification=None,
            routing=None,
            resolution=None,
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
