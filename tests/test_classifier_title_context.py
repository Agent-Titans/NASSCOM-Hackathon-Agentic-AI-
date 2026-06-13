"""Classifier uses ticket title + description together."""
from __future__ import annotations

from src.agents.classifier import ClassifierAgent
from src.models.schemas import SanitizedText


def test_build_classification_text_joins_title_and_body():
    san = SanitizedText(text="Body details here.", blocked=False, redaction_count=0)
    text = ClassifierAgent.build_classification_text(
        san, title="Cosmos DB RU Throttling"
    )
    assert text.startswith("Cosmos DB RU Throttling")
    assert "Body details here." in text


def test_finalize_sees_siem_marker_from_title_only():
    san = SanitizedText(
        text=(
            "Workspace producing 4000+ false positive alerts per hour "
            "from custom KQL correlation rule."
        ),
        blocked=False,
        redaction_count=0,
    )
    cat = ClassifierAgent().classify(
        san,
        similar=None,
        title="Sentinel SIEM Correlation Rule False Positive Flood",
    )
    assert cat.use_case_category == "Security"


def test_finalize_sees_db_marker_from_title_only():
    san = SanitizedText(
        text="Payroll database inaccessible for 2000 users across client tenants.",
        blocked=False,
        redaction_count=0,
    )
    cat = ClassifierAgent().classify(
        san,
        similar=None,
        title="Oracle RAC Node Eviction ORA-29740",
    )
    assert cat.use_case_category == "Database"
