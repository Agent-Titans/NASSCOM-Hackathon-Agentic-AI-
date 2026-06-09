"""
Notification service — logs Hand outcome (email in Phase B).

O(1) per ticket — no LLM.
"""
from __future__ import annotations

import logging

from src.models.schemas import SupervisorDecision

logger = logging.getLogger(__name__)


class NotificationService:
    def send_hand_message(
        self, ticket_id: str, decision: SupervisorDecision, requester_email: str
    ) -> None:
        hand_names = {"1": "self-help steps", "2": "team routing", "3": "specialist review"}
        msg = hand_names.get(decision.hand, "update")
        logger.info(
            "Notify %s | ticket=%s | Hand %s (%s)",
            requester_email,
            ticket_id,
            decision.hand,
            msg,
        )
