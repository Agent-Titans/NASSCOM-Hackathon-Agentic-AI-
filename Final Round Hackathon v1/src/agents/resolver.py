"""
Resolver agent — demo knowledge base now; full Chroma RAG in Phase 3.

Playbook lookup: O(p) over small pattern list (p ≈ 10).
"""
from __future__ import annotations

import re
from typing import List, Tuple

from src.models.schemas import ClassificationResult, ResolutionResult, RoutingResult, SanitizedText

# (regex pattern, steps, similarity, citations) — highest similarity wins
_DEMO_PLAYBOOKS: List[Tuple[re.Pattern[str], List[str], float, List[str]]] = [
    (
        re.compile(r"password|forgot|login|reset|mfa|locked out|access", re.I),
        [
            "Open the company password portal.",
            "Choose **Forgot password** and verify your identity.",
            "Follow the email link to set a new password (12+ characters).",
            "Sign in again; if MFA fails, contact Identity from this ticket.",
        ],
        0.90,
        ["KB-ACCESS-001", "TICKET-1042"],
    ),
    (
        re.compile(r"printer|print|toner|paper jam", re.I),
        [
            "Confirm the printer is online and has paper/toner.",
            "Remove jammed paper following the panel guide.",
            "Reinstall the driver from the internal software catalog.",
            "If the queue is stuck, clear print spooler and retry.",
        ],
        0.82,
        ["KB-HW-014", "TICKET-2201"],
    ),
    (
        re.compile(r"vpn|wifi|network|internet|dns|connection", re.I),
        [
            "Restart VPN client and re-authenticate.",
            "Forget and rejoin Wi‑Fi using corporate credentials.",
            "Run built-in network diagnostics and note error codes.",
        ],
        0.78,
        ["KB-NET-007"],
    ),
]


class ResolverAgent:
    def resolve(
        self,
        sanitized: SanitizedText,
        classification: ClassificationResult,
        routing: RoutingResult,
    ) -> ResolutionResult:
        if sanitized.blocked or not sanitized.text:
            return ResolutionResult(low_grounding=True, similarity_score=0.0)

        text = sanitized.text
        best_steps: List[str] = []
        best_sim = 0.35
        best_cites: List[str] = []
        matched = False

        # Linear scan of playbooks — small p, fast for demo.
        for pattern, steps, sim, cites in _DEMO_PLAYBOOKS:
            if pattern.search(text):
                if sim > best_sim:
                    best_sim = sim
                    best_steps = steps
                    best_cites = cites
                    matched = True

        if not matched:
            best_steps = [
                f"Your request was classified as **{classification.use_case_category}**.",
                f"The **{routing.department_queue}** team will use internal runbooks.",
                "Add screenshots or error codes in a comment to speed resolution.",
            ]
            return ResolutionResult(
                steps=best_steps,
                citations=[],
                low_grounding=True,
                similarity_score=best_sim,
            )

        # Strong playbook match — allow Hand 1 when Supervisor score is high enough.
        return ResolutionResult(
            steps=best_steps,
            citations=best_cites,
            low_grounding=False,
            similarity_score=best_sim,
        )
