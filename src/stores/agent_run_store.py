"""AgentRun persistence — LLD pipeline step success flags."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.db.models import AgentRun, Ticket


class AgentRunStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def begin(self, ticket: Ticket) -> AgentRun:
        """Create AgentRun row at pipeline start (all flags default False)."""
        run = AgentRun(ticket_id=ticket.ticket_id)
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def mark_guardrail(self, run: AgentRun, *, ok: bool) -> None:
        run.guardrail_ok = ok
        self.session.commit()

    def mark_classification(self, run: AgentRun, *, ok: bool) -> None:
        run.classification_ok = ok
        self.session.commit()

    def mark_routing(self, run: AgentRun, *, ok: bool) -> None:
        run.routing_ok = ok
        self.session.commit()

    def mark_resolver(self, run: AgentRun, *, ok: bool) -> None:
        run.resolver_ok = ok
        self.session.commit()

    def mark_supervisor(self, run: AgentRun, *, ok: bool) -> None:
        run.supervisor_ok = ok
        self.session.commit()
