"""Network ops classification overrides (LB, gateway, proxy)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.classifier import ClassifierAgent


def test_load_balancer_promoted_from_application_to_network():
    text = (
        "High CPU latency on load balancer nodes. Users seeing 504 Gateway Timeout "
        "on checkout after traffic spike this morning."
    )
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Network"


def test_gateway_timeout_promoted_from_application_to_network():
    cat = ClassifierAgent._finalize_category(
        "Application",
        "Reverse proxy returning 502 bad gateway; nginx upstream health checks failing.",
    )
    assert cat == "Network"
