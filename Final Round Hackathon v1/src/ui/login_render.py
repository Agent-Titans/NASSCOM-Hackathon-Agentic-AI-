"""Login — isolated welcome-scope + workspace-scope authentication gate."""
from __future__ import annotations

import html

import streamlit as st

from src.config.brand import PRODUCT_NAME, ROLE_DISPLAY, TAGLINE
from src.db.models import User
from src.db.session import get_session_factory
from src.ui.login_theme import login_css

_FEATURE_CARDS = (
    ("badge-instant", "Instant", "Instant Resolution",
     "Instant RAG-grounded self-help validation for direct user tracking."),
    ("badge-automated", "Automated", "Intelligent Routing",
     "Deterministic queue mapping with active SLA monitoring optimization."),
    ("badge-escalated", "Escalated", "Governed Escalation",
     "Policy-driven manual escalation matrix handling complex operational anomalies."),
)

_GATEWAY_TRACKS: list[tuple[str, str, str]] = [
    ("employee", "Employee Portal", "Submit service requests & track resolutions."),
    ("agent", "Agent Workspace", "Triage queues and manage SLA execution tracks."),
]

# (db_email, display_title, display_subline override)
_DEMO_PROFILES: dict[str, list[tuple[str, str | None, str | None]]] = {
    "employee": [
        ("requester@demo.local", "Karan Joshi", "requester@demo.local"),
        ("emily.reed@demo.local", "Emily Reed", "emily.reed@demo.local"),
        ("james.wu@demo.local", "James Wu", "james.wu@demo.local"),
        ("sarah.kim@demo.local", "Sarah Kim", "sarah.kim@demo.local"),
        ("michael.brown@demo.local", "Michael Brown", "michael.brown@demo.local"),
    ],
    "agent": [
        ("hardware@demo.local", "Alex Chen · Hardware", "hardware@demo.local"),
        ("software@demo.local", "Marcus Lee · Software", "software@demo.local"),
        ("network@demo.local", "Priya Nair · Network", "network@demo.local"),
        ("secops@demo.local", "Sam Ortiz · SecOps", "secops@demo.local"),
        ("identity@demo.local", "Jordan Kim · Identity", "identity@demo.local"),
        ("dba@demo.local", "Riley Park · DBA", "dba@demo.local"),
        ("storage@demo.local", "Casey Morgan · Storage", "storage@demo.local"),
        ("admin@demo.local", "Global System Admin", "admin@demo.local"),
    ],
}

_VALID_TRACKS = frozenset({"employee", "agent"})
_TRACK_TRIGGER_KEYS = ("track_1_trigger", "track_2_trigger")


def _init_theme_state() -> bool:
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    return bool(st.session_state.dark_mode)


def _theme_toggle() -> bool:
    _, right = st.columns([5, 1])
    with right:
        dark = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.get("dark_mode", False),
            key="login_dark_mode_toggle",
        )
    st.session_state.dark_mode = dark
    return dark


def _clear_picker_state(*, track: bool = True) -> None:
    if track:
        st.session_state.pop("current_track", None)
    st.session_state.pop("auth_pick_user_id", None)
    st.session_state.pop("auth_login_error", None)


def _clear_query_keys(*keys: str) -> None:
    try:
        for key in keys:
            if key in st.query_params:
                del st.query_params[key]
    except Exception:
        st.query_params.clear()


def _profiles_for_track(users: list[User], track: str) -> list[tuple[User, str | None, str | None]]:
    by_email = {u.email: u for u in users}
    out: list[tuple[User, str | None, str | None]] = []
    for email, custom_title, display_sub in _DEMO_PROFILES.get(track, []):
        if email in by_email:
            out.append((by_email[email], custom_title, display_sub))
    return out


def _profile_tile_copy(u: User, custom_title: str | None, display_sub: str | None) -> tuple[str, str]:
    if custom_title:
        title = custom_title
    else:
        role = ROLE_DISPLAY.get(u.role, u.role)
        title = f"{role} · {u.department}" if u.department else role
    subline = display_sub or u.email
    return title, subline


def _complete_login(users: list[User]) -> None:
    track = st.session_state.get("current_track")
    if track not in _VALID_TRACKS:
        st.session_state["auth_login_error"] = "Select a workspace track first."
        st.rerun()

    profiles = _profiles_for_track(users, track)
    if not profiles:
        st.session_state["auth_login_error"] = "No demo profiles available for this track."
        st.rerun()

    pick_id = st.session_state.get("auth_pick_user_id")
    selected: User | None = None
    for u, _title, _sub in profiles:
        if u.user_id == pick_id:
            selected = u
            break
    if selected is None:
        selected = profiles[0][0]

    st.session_state["user"] = {
        "user_id": selected.user_id,
        "email": selected.email,
        "role": selected.role,
        "department": selected.department,
    }
    st.session_state["auth_user"] = selected.email
    st.session_state["auth_user_id"] = selected.user_id
    st.session_state["admin_via_agent"] = (
        track == "agent" and selected.email == "admin@demo.local"
    )

    if selected.role == "requester":
        st.session_state["page"] = "portal"
        st.session_state["portal_view"] = "home"
    else:
        st.session_state["page"] = "overview"

    st.session_state.pop("signed_in", None)
    _clear_picker_state()
    _clear_query_keys("portal_view", "portal_ticket")
    st.rerun()


def _gate_header_html(*, eyebrow: str, heading: str, desc: str, error: str | None) -> str:
    brand = html.escape(PRODUCT_NAME)
    err = f'<p class="gateway-error">{html.escape(error)}</p>' if error else ""
    return (
        '<div class="workspace-scope workspace-gate-header">'
        f'<p class="gate-brand-line"><span class="gate-brand">{brand}</span>'
        '<span class="gate-brand-dot">.</span></p>'
        f'<p class="gate-eyebrow">{html.escape(eyebrow)}</p>'
        f'<h1 class="gateway-heading">{html.escape(heading)}</h1>'
        f'<p class="gateway-desc">{html.escape(desc)}</p>'
        f"{err}"
        "</div>"
    )


def _tile_card_html(title: str, desc: str) -> str:
    return (
        '<div class="gate-tile-row workspace-scope">'
        '<div class="gateway-tile-card">'
        f'<div class="tile-title">{html.escape(title)}</div>'
        f'<div class="tile-desc">{html.escape(desc)}</div>'
        '<span class="tile-chevron" aria-hidden="true">›</span>'
        "</div></div>"
    )


def _overlay_button(key: str) -> bool:
    return st.button("", key=key, type="secondary")


def _render_overlay_tile(title: str, desc: str, trigger_key: str) -> bool:
    st.markdown(_tile_card_html(title, desc), unsafe_allow_html=True)
    return _overlay_button(trigger_key)


def _render_track_gateway() -> None:
    error = st.session_state.get("auth_login_error")
    st.markdown(
        _gate_header_html(
            eyebrow="WORKSPACE GATEWAY",
            heading="Select Workspace",
            desc="Choose your operational track to enter the routing platform.",
            error=error,
        ),
        unsafe_allow_html=True,
    )
    for idx, (track_id, title, desc) in enumerate(_GATEWAY_TRACKS):
        trigger_key = _TRACK_TRIGGER_KEYS[idx]
        if _render_overlay_tile(title, desc, trigger_key):
            st.session_state["current_track"] = track_id
            st.session_state.pop("auth_pick_user_id", None)
            st.session_state.pop("auth_login_error", None)
            st.rerun()

    if st.button("← Back to home", key="gate_logout", type="tertiary"):
        st.session_state["signed_in"] = False
        st.session_state["current_track"] = None
        _clear_picker_state()
        st.rerun()

    st.markdown(
        '<p class="workspace-scope gateway-copyright">'
        "© 2026 ClearHand Systems. All rights reserved.</p>",
        unsafe_allow_html=True,
    )


def _render_sandbox_vault(users: list[User]) -> None:
    track = st.session_state["current_track"]
    profiles = _profiles_for_track(users, track)
    error = st.session_state.get("auth_login_error")

    st.markdown(
        _gate_header_html(
            eyebrow="DEMO SANDBOX",
            heading="Choose Profile",
            desc="Select an identity below to simulate live pipeline execution.",
            error=error,
        ),
        unsafe_allow_html=True,
    )
    if not profiles:
        st.markdown('<p class="gateway-empty">No demo profiles for this track.</p>', unsafe_allow_html=True)
    else:
        for u, custom_title, display_sub in profiles:
            title, subline = _profile_tile_copy(u, custom_title, display_sub)
            if _render_overlay_tile(title, subline, f"profile_{u.user_id}_trigger"):
                st.session_state["auth_pick_user_id"] = u.user_id
                _complete_login(users)

    if st.button("← Back to track selection", key="gate_back_tracks", type="tertiary"):
        st.session_state["current_track"] = None
        st.session_state.pop("auth_pick_user_id", None)
        st.session_state.pop("auth_login_error", None)
        st.rerun()

    st.markdown(
        '<p class="workspace-scope gateway-copyright">'
        "© 2026 ClearHand Systems. All rights reserved.</p>",
        unsafe_allow_html=True,
    )


def _welcome_hero_html() -> str:
    name = html.escape(PRODUCT_NAME)
    tagline = html.escape(TAGLINE)
    return (
        '<div class="login-page-root welcome-scope">'
        '<div class="hero-container">'
        '<p class="login-eyebrow">WELCOME TO</p>'
        f'<h1 class="login-title"><span class="brand-name">{name}</span>'
        '<span class="brand-dot">.</span></h1>'
        f'<p class="login-tagline">{tagline}</p>'
        "</div>"
    )


def _welcome_tail_html() -> str:
    cards = []
    for badge_cls, badge_label, title, desc in _FEATURE_CARDS:
        cards.append(
            '<div class="product-card">'
            f'<span class="product-badge {badge_cls}">{html.escape(badge_label)}</span>'
            f'<h3 class="product-card-title">{html.escape(title)}</h3>'
            f'<p class="product-card-desc">{html.escape(desc)}</p>'
            "</div>"
        )
    grid = "".join(cards)
    return (
        '<div class="welcome-scope welcome-body">'
        f'<div class="product-grid">{grid}</div>'
        '<div class="login-footer">© 2026 ClearHand Systems. All rights reserved.</div>'
        "</div></div>"
    )


def _render_auth_chrome() -> bool:
    """Shared dark-mode toggle + scoped CSS. Returns current dark flag."""
    st.markdown('<div class="login-toggle-wrap">', unsafe_allow_html=True)
    dark = _theme_toggle()
    st.markdown("</div>", unsafe_allow_html=True)
    st.html(login_css(dark))
    return dark


def render_welcome_step() -> None:
    _render_auth_chrome()
    st.markdown(_welcome_hero_html(), unsafe_allow_html=True)

    if st.button("Sign In", key="welcome_sign_in", type="primary"):
        st.session_state["signed_in"] = True
        st.session_state["current_track"] = None
        _clear_picker_state(track=False)
        st.rerun()

    st.markdown(_welcome_tail_html(), unsafe_allow_html=True)


def render_workspace_step(users: list[User]) -> None:
    _render_auth_chrome()

    _, center, _ = st.columns([1, 1.15, 1])
    with center:
        track = st.session_state.get("current_track")
        if track not in _VALID_TRACKS:
            _render_track_gateway()
        else:
            _render_sandbox_vault(users)


def render_login_page() -> None:
    if "user" in st.session_state:
        return

    Session = get_session_factory()
    with Session() as session:
        users = session.query(User).order_by(User.role, User.email).all()

    if not st.session_state.get("signed_in"):
        render_welcome_step()
        return

    if not users:
        st.error("No accounts found. Run `python scripts/seed_users.py`")
        return

    render_workspace_step(users)
