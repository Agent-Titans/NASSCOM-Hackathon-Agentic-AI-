"""SecOps-owned Routing Specialists desk — human-in-the-loop misroute correction."""

from __future__ import annotations

SPECIALISTS_QUEUE = "Specialists"
SPECIALISTS_DISPLAY = "Routing Specialists"
SPECIALISTS_CAPTION = "Operated by SecOps team"
STATUS_ROUTING_REVIEW = "ROUTING_REVIEW"

EVENT_SPECIALIST_REQUESTED = "specialist_requested"
EVENT_SPECIALIST_REROUTED = "specialist_rerouted"
EVENT_SPECIALIST_KEPT_SECOPS = "specialist_kept_secops"

MIN_REASON_CHARS = 15
