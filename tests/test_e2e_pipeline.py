"""End-to-end DB pipeline — security ticket must be Hand 3."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.models import AuditLog, User
from src.db.session import get_session_factory, init_db
from src.services.ticket_service import TicketService
from src.stores.ticket_store import TicketStore


def test_security_ticket_hand3():
    init_db()
    Session = get_session_factory()
    with Session() as session:
        user = session.query(User).filter(User.email == "requester@demo.local").first()
        if user is None:
            user = User(email="e2e@demo.local", role="requester")
            session.add(user)
            session.commit()
            session.refresh(user)
        ticket = TicketStore(session).create(
            user,
            "VPN breach",
            "Possible security breach on VPN - unauthorized access detected",
            "high",
        )
        svc = TicketService(session)
        # Legitimate security incident text — Layer 2 must allow (not an injection).
        with patch.object(
            svc.guardrail.gemini,
            "scan_prompt_injection",
            return_value="SECURITY_OK",
        ):
            result = svc.process_ticket(ticket)
        session.refresh(ticket)
        assert result.decision.hand == "3"
        assert ticket.hand == "3"
        assert ticket.department_queue == "SecOps"
        audits = (
            session.query(AuditLog)
            .filter(AuditLog.ticket_id == ticket.ticket_id)
            .all()
        )
        agents = {a.agent for a in audits if a.agent}
        assert agents >= {
            "guardrail",
            "retrieval",
            "classifier",
            "router",
            "resolver",
            "supervisor",
        }
