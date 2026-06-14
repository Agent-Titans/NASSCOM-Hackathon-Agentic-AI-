"""Clickable retrieval reference links on ticket detail pages."""
from __future__ import annotations

from collections.abc import Callable

import streamlit as st
from sqlalchemy.orm import Session

from src.models.schemas import RetrievalReference
from src.services.reference_ticket_loader import load_reference_ticket, resolve_reference_link


def _button_label(ref: RetrievalReference) -> str:
    pct = int(round(ref.score * 100))
    source = "RAG" if ref.source == "rag" else "User ticket"
    if ref.title:
        short = ref.title[:42] + ("…" if len(ref.title) > 42 else "")
        return f"↗ {ref.label} — {short} ({pct}% · {source})"
    return f"↗ {ref.label} ({pct}% · {source})"


def render_resolution_references(
    session: Session,
    references: list[RetrievalReference],
    *,
    owner_ticket_id: str,
    key_prefix: str,
    wrap: Callable[[str], str],
    open_reference: Callable[[str, str], None],
) -> None:
    """Best RAG + user retrieval hits used for hand / confidence."""
    resolved: list[tuple[RetrievalReference, str]] = []
    seen: set[str] = set()
    for ref in references:
        ref_id = resolve_reference_link(session, ref.ticket_id or ref.label)
        if not ref_id or ref_id in seen:
            continue
        if not load_reference_ticket(session, ref_id):
            continue
        seen.add(ref_id)
        resolved.append((ref, ref_id))

    if not resolved:
        return

    st.markdown(
        wrap(
            '<div class="itsm-section"><p class="itsm-section-title">'
            "Referenced similar tickets</p>"
        ),
        unsafe_allow_html=True,
    )
    for idx, (ref, ref_id) in enumerate(resolved):
        if st.button(
            _button_label(ref),
            key=f"{key_prefix}_ref_{owner_ticket_id}_{idx}",
            type="tertiary",
        ):
            open_reference(ref_id, owner_ticket_id)
    st.markdown(wrap("</div>"), unsafe_allow_html=True)
