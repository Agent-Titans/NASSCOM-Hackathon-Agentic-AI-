"""Demo agent presence indicators for admin team cards (Teams-style)."""
from __future__ import annotations

import random
import time
from typing import Literal

import streamlit as st

from src.config.demo_profiles import AGENT_QUEUE_LABELS, demo_person_name

PresenceStatus = Literal["available", "away", "offline"]

_PRESENCE_STATUSES: tuple[PresenceStatus, ...] = ("available", "away", "offline")
_PRESENCE_WEIGHTS = (0.52, 0.28, 0.20)
_PRESENCE_LABELS = {
    "available": "Available",
    "away": "Away",
    "offline": "Offline",
}
_REFRESH_SECONDS = 180
_STATE_KEY = "admin_presence_map"
_UPDATED_KEY = "admin_presence_updated_at"


def roster_emails() -> list[str]:
    return [email for email in AGENT_QUEUE_LABELS if email != "admin@employee"]


def members_for_team(team_name: str) -> list[tuple[str, str]]:
    """Return (display_name, email) for agents on this dashboard team card."""
    if team_name == "Triage Queue":
        return [
            (demo_person_name(email), email)
            for email in AGENT_QUEUE_LABELS
            if email != "admin@employee"
        ]

    dept = team_name.removesuffix(" Team") if team_name.endswith(" Team") else team_name
    return [
        (demo_person_name(email), email)
        for email, d in AGENT_QUEUE_LABELS.items()
        if email != "admin@employee" and d == dept
    ]


def refresh_presence_states() -> dict[str, PresenceStatus]:
    """Randomize presence every few minutes; stable between refreshes."""
    now = time.time()
    last = float(st.session_state.get(_UPDATED_KEY, 0.0))
    emails = roster_emails()
    states: dict[str, PresenceStatus] = dict(st.session_state.get(_STATE_KEY, {}))

    due = (now - last) >= _REFRESH_SECONDS or not states
    if due:
        states = {
            email: random.choices(_PRESENCE_STATUSES, weights=_PRESENCE_WEIGHTS, k=1)[0]
            for email in emails
        }
        st.session_state[_STATE_KEY] = states
        st.session_state[_UPDATED_KEY] = now
    else:
        for email in emails:
            if email not in states:
                states[email] = random.choices(
                    _PRESENCE_STATUSES, weights=_PRESENCE_WEIGHTS, k=1
                )[0]
        st.session_state[_STATE_KEY] = states

    return states


def team_members_html(team_name: str, presence: dict[str, PresenceStatus]) -> str:
    members = members_for_team(team_name)
    if not members:
        return ""

    rows = []
    for name, email in members:
        status = presence.get(email, "offline")
        label = _PRESENCE_LABELS[status]
        rows.append(
            f'<div class="admin-member-row">'
            f'<span class="admin-presence-dot presence-{status}" '
            f'title="{label}"></span>'
            f'<span class="admin-member-name">{name}</span>'
            f'<span class="admin-presence-label">{label}</span>'
            f"</div>"
        )
    return (
        '<div class="admin-team-members">'
        '<p class="admin-team-members-title">Team members</p>'
        + "".join(rows)
        + "</div>"
    )


def schedule_presence_rerun() -> None:
    """Rerun dashboard periodically so presence states rotate."""
    import streamlit.components.v1 as components

    components.html(
        f"""
        <script>
        (function() {{
          const intervalMs = {_REFRESH_SECONDS * 1000};
          if (window.__intelliqPresenceInterval) return;
          window.__intelliqPresenceInterval = setInterval(function() {{
            window.parent.postMessage({{type: "streamlit:rerun"}}, "*");
          }}, intervalMs);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
