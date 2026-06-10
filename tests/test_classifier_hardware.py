"""Hardware topic classification overrides."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.classifier import ClassifierAgent
from src.models.schemas import SanitizedText


def test_charger_classified_as_infrastructure():
    cat = ClassifierAgent._finalize_category(
        "Network",
        "need to replace laptop charger as its not working",
    )
    assert cat == "Infrastructure"
