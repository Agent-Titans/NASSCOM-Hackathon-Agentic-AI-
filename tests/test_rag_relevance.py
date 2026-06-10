"""RAG relevance guard — block wrong-topic playbook reuse."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.schemas import ClassificationResult, ResolutionResult, SimilarTicketMatch
from src.services.rag_gate import evaluate_rag_match
from src.services.rag_relevance import is_rag_relevant, topic_buckets


def _vpn_match(score: float = 0.66) -> SimilarTicketMatch:
    return SimilarTicketMatch(
        ticket_id="d29dfe5b",
        title="VPN issue",
        similarity_score=score,
        classification=ClassificationResult(
            "Network", subcategory="similar_ticket", source="rag"
        ),
        resolution=ResolutionResult(
            steps=[
                "Restart VPN client and re-authenticate.",
                "Forget and rejoin Wi-Fi using corporate credentials.",
            ],
            low_grounding=False,
        ),
        department_queue="Network",
        source="chroma",
        source_hand="2",
    )


def test_topic_buckets_charger_is_hardware():
    topics = topic_buckets("laptop charger replace — not working")
    assert "hardware" in topics
    assert "network" not in topics


def test_charger_query_rejects_vpn_match():
    query = "laptop charger replace\nneed to replace laptop charger as its not working"
    ok, reason = is_rag_relevant(query, _vpn_match())
    assert not ok
    assert reason == "topic_mismatch"


def test_rag_gate_rejects_vpn_for_charger():
    query = "laptop charger replace\nneed to replace laptop charger as its not working"
    gate = evaluate_rag_match(_vpn_match(), query_text=query)
    assert gate.raw is not None
    assert gate.trusted is None
    assert gate.reason == "topic_mismatch"


def test_vpn_query_accepts_vpn_match():
    query = "unable to connect to VPN at all from morning"
    gate = evaluate_rag_match(_vpn_match(), query_text=query)
    assert gate.trusted is not None
    assert gate.reason == "trusted"


def test_airflow_reference_relevant():
    from src.services.rag_relevance import is_reference_relevant

    query = "airflow job logs and audit log not visible in UI"
    assert is_reference_relevant(
        query,
        ticket_id="ent-h2-07",
        title="Airflow job and audit logs not visible",
        score=0.72,
        source="rag",
        category="Application",
    )


def test_python_install_not_referenced_for_airflow():
    from src.services.rag_relevance import is_reference_relevant

    query = "airflow job logs and audit log not visible"
    assert not is_reference_relevant(
        query,
        ticket_id="195ce4f7",
        title="unable to install python software",
        score=0.61,
        source="user",
        category="Application",
    )
