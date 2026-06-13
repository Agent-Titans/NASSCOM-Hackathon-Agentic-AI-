#!/usr/bin/env python3
"""Smoke test: Routing Specialists desk end-to-end (no browser)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.specialists import SPECIALISTS_QUEUE, STATUS_ROUTING_REVIEW
from src.db.models import User
from src.db.session import get_session_factory, init_db
from src.services.specialists_desk_service import (
    get_specialist_context,
    list_specialists_queue,
    request_specialist_review,
    reroute_from_specialists,
)
from src.services.ticket_service import TicketService
from src.stores.ticket_store import TicketStore


def main() -> int:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requester = session.query(User).filter_by(email="pallavi@user").first()
        sw_agent = session.query(User).filter_by(email="subbu@employee").first()
        secops = session.query(User).filter_by(email="narsimha@employee").first()
        if not all([requester, sw_agent, secops]):
            print("FAIL: demo users missing")
            return 1

        ticket = TicketStore(session).create(
            requester,
            "Misrouted VPN ticket in Software queue",
            "Always On VPN split tunnel not routing Azure private endpoints — network issue.",
            urgency="high",
        )
        TicketService(session).process_ticket(ticket)
        session.refresh(ticket)
        print(f"1) AI routed: H{ticket.hand} / {ticket.department_queue}")

        # Simulate misroute in Software queue for specialist-desk flow validation
        ticket.department_queue = "Software"
        ticket.hand = "2"
        ticket.status = "ROUTED"
        session.commit()
        session.refresh(ticket)
        print(f"1b) Simulated misroute: H{ticket.hand} / {ticket.department_queue}")

        ok, msg = request_specialist_review(
            session,
            ticket,
            sw_agent,
            "This is a network VPN routing issue, not application software.",
        )
        if not ok:
            print(f"FAIL send to specialists: {msg}")
            return 1
        session.refresh(ticket)
        print(f"2) Specialists queue: {ticket.department_queue} / {ticket.status}")
        assert ticket.department_queue == SPECIALISTS_QUEUE
        assert ticket.status == STATUS_ROUTING_REVIEW

        queue = list_specialists_queue(session)
        assert any(t.ticket_id == ticket.ticket_id for t in queue)
        print(f"3) SecOps specialists inbox count: {len(queue)}")

        ctx = get_specialist_context(session, ticket.ticket_id)
        print(f"4) Context: from={ctx['original_department']} reason={ctx['reason'][:40]}…")

        ok2, msg2 = reroute_from_specialists(session, ticket, secops, "Network")
        if not ok2:
            print(f"FAIL reroute: {msg2}")
            return 1
        session.refresh(ticket)
        print(f"5) Rerouted to: {ticket.department_queue} / {ticket.status}")
        assert ticket.department_queue == "Network"
        assert ticket.status == "ROUTED"

        TicketStore(session).resolve(ticket)
        print("OK: Routing Specialists smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
