"""Login — SAARTHI welcome home + email/password sign-in."""
from __future__ import annotations

import html

import streamlit as st

from src.config.brand import ORG_NAME, PRODUCT_ABBREVIATION, PRODUCT_NAME, TAGLINE
from src.config.demo_auth import (
    AGENT_WORKSPACE_EMAILS,
    DEFAULT_DEMO_PASSWORD,
    EMPLOYEE_PORTAL_EMAILS,
    normalize_email,
    verify_demo_password,
)
from src.db.models import User
from src.db.session import get_session_factory
from src.services.retrieval_bootstrap import retrieval_warm_status
from src.ui.login_theme import login_css

_FEATURE_CARDS = (
    ("badge-instant", "Hand 1", "Self-Help Resolution",
     "RAG-grounded steps employees can try immediately — no queue wait."),
    ("badge-automated", "Hand 2", "Smart Routing",
     "Auto-route to the right team with capacity-aware assignment."),
    ("badge-escalated", "Hand 3", "Expert Escalation",
     "Policy-driven specialist review when confidence is low."),
)


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


def _clear_auth_state() -> None:
    for key in (
        "show_signin",
        "auth_login_error",
        "signed_in",
        "current_track",
        "auth_pick_user_id",
    ):
        st.session_state.pop(key, None)


def _clear_query_keys(*keys: str) -> None:
    try:
        for key in keys:
            if key in st.query_params:
                del st.query_params[key]
    except Exception:
        st.query_params.clear()


def _session_login(user: User) -> None:
    email = normalize_email(user.email)
    st.session_state["user"] = {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "department": user.department,
    }
    st.session_state["auth_user"] = user.email
    st.session_state["auth_user_id"] = user.user_id
    st.session_state["admin_via_agent"] = (
        user.role == "admin" and email == "admin@employee"
    )

    if user.role in ("requester", "employee"):
        st.session_state["page"] = "portal"
        st.session_state["portal_view"] = "home"
        from src.services.retrieval_bootstrap import start_retrieval_warm_background

        start_retrieval_warm_background(delay_seconds=0.5, api_embeds=True)
    else:
        st.session_state["page"] = "overview"

    _clear_auth_state()
    _clear_query_keys("portal_view", "portal_ticket")
    st.rerun()


def _brand_wordmark_html(*, size: str = "hero") -> str:
    name = html.escape(PRODUCT_NAME)
    return (
        f'<span class="brand-wordmark brand-wordmark-{size}">'
        f'<span class="brand-name">{name}</span><span class="brand-dot">.</span>'
        "</span>"
    )


def _brand_title_html(*, eyebrow: str = "") -> str:
    eyebrow_html = (
        f'<p class="login-eyebrow">{html.escape(eyebrow)}</p>' if eyebrow else ""
    )
    return (
        f'<div class="brand-lockup">{eyebrow_html}'
        f'<p class="login-title">{_brand_wordmark_html(size="hero")}</p>'
        "</div>"
    )


def _welcome_hero_html() -> str:
    tagline = html.escape(TAGLINE)
    caption = html.escape(PRODUCT_ABBREVIATION)
    warm = retrieval_warm_status()
    warm_html = ""
    if warm == "running":
        warm_html = (
            '<p class="login-warm-pill" aria-live="polite">'
            '<span class="login-warm-dot"></span> Preparing routing engine…'
            "</p>"
        )
    return (
        '<div class="login-page-root welcome-scope">'
        '<div class="hero-container">'
        f"{_brand_title_html(eyebrow='WELCOME TO')}"
        f'<p class="login-tagline">{tagline}</p>'
        f'<p class="login-caption">{caption}</p>'
        f"{warm_html}"
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
    org = html.escape(ORG_NAME)
    return (
        '<div class="welcome-scope welcome-body">'
        f'<div class="product-grid">{"".join(cards)}</div>'
        f'<div class="login-footer">© 2026 {org}. All rights reserved.</div>'
        "</div></div>"
    )


def _signin_topnav_html() -> str:
    """Brand row above the card — SAARTHI wordmark."""
    return (
        '<span class="signin-layout-marker" aria-hidden="true"></span>'
        '<div class="signin-scope signin-topnav-outside">'
        f'<div class="signin-topnav">{_brand_wordmark_html(size="nav")}</div>'
        "</div>"
    )


def _signin_card_top_html() -> str:
    return (
        '<span class="signin-card-shell-marker" aria-hidden="true"></span>'
        '<div class="signin-scope signin-card-top">'
        '<div class="signin-lock-icon" aria-hidden="true">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
        'stroke="#fff" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/>'
        '<path d="M8 11V8a4 4 0 1 1 8 0v3"/></svg></div>'
        '<p class="signin-heading">Sign In</p>'
        '<p class="signin-subtitle">Enter your credentials to access your account</p>'
        "</div>"
    )


def _render_auth_chrome(scope: str = "welcome") -> bool:
    dark = bool(st.session_state.get("dark_mode", False))
    if scope != "signin":
        st.markdown('<div class="login-toggle-wrap">', unsafe_allow_html=True)
        dark = _theme_toggle()
        st.markdown("</div>", unsafe_allow_html=True)
    st.html(login_css(dark))
    return dark


def render_welcome_step() -> None:
    _render_auth_chrome()
    st.markdown(_welcome_hero_html(), unsafe_allow_html=True)

    if st.button("Sign In", key="welcome_sign_in", type="primary"):
        st.session_state["show_signin"] = True
        st.session_state.pop("auth_login_error", None)
        st.rerun()

    st.markdown(_welcome_tail_html(), unsafe_allow_html=True)


def _lookup_user(users: list[User], email: str) -> User | None:
    target = normalize_email(email)
    for user in users:
        if normalize_email(user.email) == target:
            return user
    return None


def render_signin_step(users: list[User]) -> None:
    _render_auth_chrome("signin")

    st.markdown(_signin_topnav_html(), unsafe_allow_html=True)
    st.markdown(_signin_card_top_html(), unsafe_allow_html=True)

    error = st.session_state.get("auth_login_error")
    if error:
        st.markdown(
            f'<p class="signin-scope signin-error">{html.escape(error)}</p>',
            unsafe_allow_html=True,
        )

    with st.form("signin_form", clear_on_submit=False, border=False):
        st.markdown(
            '<span class="signin-form-marker" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        email = st.text_input(
            "Email Address",
            placeholder="you@example.com",
            key="signin_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            key="signin_password",
        )
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if submitted:
            if not email.strip() or not password:
                st.session_state["auth_login_error"] = "Email and password are required."
                st.rerun()

            if not verify_demo_password(password):
                st.session_state["auth_login_error"] = "Invalid email or password."
                st.rerun()

            user = _lookup_user(users, email)
            if user is None:
                st.session_state["auth_login_error"] = (
                    "Unknown email. Use your assigned employee or agent address."
                )
                st.rerun()

            norm = normalize_email(user.email)
            if norm in EMPLOYEE_PORTAL_EMAILS and user.role not in ("requester", "employee"):
                st.session_state["auth_login_error"] = "Invalid email or password."
                st.rerun()
            if norm in AGENT_WORKSPACE_EMAILS and user.role not in ("assignee", "admin"):
                st.session_state["auth_login_error"] = "Invalid email or password."
                st.rerun()

            _session_login(user)


def render_login_page() -> None:
    if "user" in st.session_state:
        return

    if st.session_state.get("show_signin"):
        Session = get_session_factory()
        with Session() as session:
            users = session.query(User).order_by(User.role, User.email).all()
        if not users:
            st.error("No accounts found. Run `python scripts/seed_users.py`")
            return
        render_signin_step(users)
        return

    render_welcome_step()
