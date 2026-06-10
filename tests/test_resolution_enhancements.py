"""Tests for feedback escalation, steps codec, security short-circuit."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.enterprise_rag_corpus import ENTERPRISE_RAG_CORPUS, load_enterprise_corpus
from src.models.schemas import ClassificationResult, ResolutionResult, RoutingResult, SanitizedText
from src.services.resolution_steps_codec import (
    decode_steps,
    encode_steps,
    is_schema_junk_steps,
)


def test_enterprise_corpus_counts_and_h1_simplicity():
    corpus = load_enterprise_corpus()
    assert len(corpus) == 30
    h1 = [e for e in corpus if e[4] == "1"]
    h2 = [e for e in corpus if e[4] == "2"]
    assert len(h1) == 15
    assert len(h2) == 15
    for entry in h1:
        text = " ".join(entry[5]).lower()
        assert "kubectl" not in text
        assert "sp_whoisactive" not in text
        assert "dcdiag" not in text


def test_steps_codec_dual_audience():
    raw = encode_steps(
        ["base"],
        steps_requester=["Clear cache", "Restart browser"],
        steps_assignee=["Collect HAR", "Check app logs"],
    )
    req, asn = decode_steps(raw)
    assert req == ["Clear cache", "Restart browser"]
    assert asn == ["Collect HAR", "Check app logs"]


def test_steps_codec_legacy_list():
    raw = encode_steps(["a", "b"])
    req, asn = decode_steps(raw)
    assert req == ["a", "b"]
    assert asn == ["a", "b"]


def test_steps_codec_rejects_schema_junk():
    assert is_schema_junk_steps(["v", "requester", "assignee"])
    raw = encode_steps(["v", "requester", "assignee"])
    req, asn = decode_steps(raw)
    assert req == []
    assert asn == []


def test_gemini_format_unwraps_nested_v2_dict(monkeypatch):
    from src.clients.gemini_client import GeminiClient
    from src.config.settings import get_settings

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    get_settings.cache_clear()
    client = GeminiClient()
    with patch.object(client, "_post") as mock_post:
        mock_post.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    '{"steps_requester": {"v": 2, "requester": '
                                    '["Check scheduler pod logs"], "assignee": '
                                    '["kubectl logs deployment/airflow-scheduler"]}, '
                                    '"steps_assignee": {"v": 2, "requester": '
                                    '["Status update"], "assignee": '
                                    '["Inspect task logs in UI"]}}'
                                )
                            }
                        ]
                    }
                }
            ]
        }
        out = client.format_resolution_audiences(
            ticket_text="airflow logs missing",
            category="Application",
            department="Software",
            hand="2",
            playbook_steps=["Verify scheduler is running", "Check worker logs"],
            citations=[],
        )
    get_settings.cache_clear()
    assert out is not None
    assert out["steps_requester"] == ["Check scheduler pod logs"]
    assert out["steps_assignee"] == ["Inspect task logs in UI"]


def test_security_short_circuit_skips_resolver_llm():
    from src.agents.router import RouterAgent
    from src.db.models import User
    from src.db.session import get_session_factory, init_db
    from src.services.ticket_service import TicketService
    from src.stores.ticket_store import TicketStore

    init_db()
    Session = get_session_factory()
    with Session() as session:
        user = session.query(User).filter(User.email == "requester@demo.local").first()
        if user is None:
            user = User(email="sec-sc@demo.local", role="requester")
            session.add(user)
            session.commit()
            session.refresh(user)
        ticket = TicketStore(session).create(
            user,
            "AWS key leak",
            "I accidentally pushed secret access key to public github",
            "high",
        )
        svc = TicketService(session)
        with patch.object(svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"):
            with patch.object(svc.resolver, "resolve") as mock_resolve:
                svc.process_ticket(ticket)
                mock_resolve.assert_not_called()
        session.refresh(ticket)
        assert ticket.hand == "3"


def test_resolution_formatter_skips_hand3():
    from src.services.resolution_formatter import ResolutionFormatter
    from src.models.schemas import SupervisorDecision

    fmt = ResolutionFormatter()
    base = ResolutionResult(
        steps=["step"],
        low_grounding=False,
        similarity_score=0.8,
    )
    out = fmt.maybe_rewrite(
        sanitized=SanitizedText("test"),
        classification=ClassificationResult("Application"),
        routing=RoutingResult("Software", "P1", 24),
        resolution=base,
        decision=SupervisorDecision(hand="3", c_total=0.4, escalation_required=True, status="HUMAN_REVIEW"),
        trusted_similar=None,
        pipeline_started_at=0.0,
    )
    assert out.steps == ["step"]
