"""Pipeline latency benchmark — LLD target: submit → Hand visible in <15s."""
from __future__ import annotations

import os
import time
from unittest.mock import patch

import pytest

from src.config.settings import get_settings
from src.db.models import User
from src.db.session import get_session_factory, init_db, reset_db_caches
from src.services.ticket_service import TicketService
from src.stores.ticket_store import TicketStore

LATENCY_BUDGET_SEC = float(os.environ.get("PIPELINE_LATENCY_BUDGET_SEC", "15"))

_BENCHMARK_TICKETS = [
    (
        "password_reset",
        "Forgot password",
        "I forgot my password and cannot login to the company portal",
    ),
    (
        "vpn_807",
        "VPN error",
        "I'm getting an Error 807 when I try to start my VPN client.",
    ),
    (
        "security_breach",
        "VPN breach",
        "Possible security breach on VPN - unauthorized access detected",
    ),
]


@pytest.fixture
def latency_db(monkeypatch, tmp_path):
    db_file = tmp_path / "latency.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        user = User(email="latency@bench", role="requester")
        session.add(user)
        session.commit()
        session.refresh(user)
        yield session, user
    get_settings.cache_clear()
    reset_db_caches()


@pytest.mark.slow
@pytest.mark.parametrize("case_id,title,description", _BENCHMARK_TICKETS)
def test_pipeline_latency_under_budget(latency_db, case_id, title, description):
    session, user = latency_db
    ticket = TicketStore(session).create(user, title, description, "medium")
    svc = TicketService(session)

    start = time.perf_counter()
    with patch.object(
        svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"
    ):
        with patch.object(svc.classifier.gemini, "classify_ticket", return_value=None):
            with patch.object(
                svc.resolver.gemini,
                "generate_resolution",
                return_value={"steps": ["Follow playbook."], "citations": []},
            ):
                result = svc.process_ticket(ticket)
    elapsed = time.perf_counter() - start

    session.refresh(ticket)
    assert result.decision is not None
    assert ticket.hand in ("1", "2", "3")
    assert elapsed < LATENCY_BUDGET_SEC, (
        f"{case_id} took {elapsed:.2f}s (budget {LATENCY_BUDGET_SEC}s)"
    )


@pytest.mark.slow
def test_pipeline_latency_p95_under_budget(latency_db):
    """Aggregate: p95 of representative tickets must stay within budget."""
    session, user = latency_db
    svc = TicketService(session)
    durations: list[float] = []

    for _case_id, title, description in _BENCHMARK_TICKETS:
        ticket = TicketStore(session).create(user, title, description, "medium")
        start = time.perf_counter()
        with patch.object(
            svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"
        ):
            with patch.object(
                svc.classifier.gemini, "classify_ticket", return_value=None
            ):
                with patch.object(
                    svc.resolver.gemini,
                    "generate_resolution",
                    return_value={"steps": ["Follow playbook."], "citations": []},
                ):
                    svc.process_ticket(ticket)
        durations.append(time.perf_counter() - start)

    durations.sort()
    p95 = durations[max(0, int(len(durations) * 0.95) - 1)]
    assert p95 < LATENCY_BUDGET_SEC, (
        f"p95 latency {p95:.2f}s exceeds budget {LATENCY_BUDGET_SEC}s "
        f"(all: {[f'{d:.2f}' for d in durations]})"
    )
