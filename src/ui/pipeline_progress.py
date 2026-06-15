"""Streamlit pipeline progress — optional stage callbacks for ticket submit."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterator, Optional

import streamlit as st

StageCallback = Callable[[str, str], None]

_STAGE_LABELS: dict[str, str] = {
    "guardrail": "Guardrail — PII redaction & injection scan",
    "retrieval": "Retrieval — similar resolved tickets (RAG)",
    "classifier": "Classifier — category & confidence",
    "router": "Router — department queue & priority",
    "resolver": "Resolver — grounded resolution steps",
    "supervisor": "Supervisor — Hand & confidence band",
    "resolution_format": "Format — requester-facing steps",
}


@contextmanager
def streamlit_pipeline_status(
    *,
    label: str = "Routing your request…",
) -> Iterator[Optional[StageCallback]]:
    """Yield an on_stage callback for TicketService.process_ticket (inside st.status)."""
    seen: set[str] = set()

    def on_stage(agent: str, phase: str) -> None:
        if phase != "complete" or agent in seen:
            return
        seen.add(agent)
        text = _STAGE_LABELS.get(agent, agent.replace("_", " ").title())
        st.write(f"✓ {text}")

    with st.status(label, expanded=True) as status:
        yield on_stage
        status.update(label="Routed successfully", state="complete", expanded=False)
