"""SaaS-style UI building blocks for IntelliQ."""
from __future__ import annotations

import html
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from src.config.brand import (
    HAND_DISPLAY,
    PRODUCT_ABBREVIATION,
    PRODUCT_NAME,
    ROLE_DISPLAY,
    TAGLINE,
)


@lru_cache(maxsize=4)
def _read_theme_css(path_str: str, mtime_ns: int) -> str:
    return Path(path_str).read_text(encoding="utf-8")


def inject_theme(css_path) -> None:
    path = Path(css_path)
    if path.exists():
        css = _read_theme_css(str(path), path.stat().st_mtime_ns)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def hand_badge_html(hand: Optional[str]) -> str:
    if not hand:
        return '<span class="badge badge-pending">Routing</span>'
    label, _, css = HAND_DISPLAY.get(hand, ("—", "", "pending"))
    cls = css.replace("hand-", "badge-")
    return f'<span class="badge {cls}">{html.escape(label)}</span>'


def sidebar_brand() -> None:
    st.markdown(
        f"""
        <div class="saas-logo">
          <h2>{html.escape(PRODUCT_NAME)}<span style="color:#818cf8">.</span></h2>
          <p>{html.escape(TAGLINE)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_user(email: str, role: str) -> None:
    role_label = ROLE_DISPLAY.get(role, role.title())
    initials = "".join(p[0].upper() for p in email.split("@")[0].split(".")[:2]) or "U"
    st.markdown(
        f"""
        <div class="saas-user-card">
          <p class="name">{html.escape(initials)} · {html.escape(email.split('@')[0])}</p>
          <p class="role">{html.escape(role_label)} workspace</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: Optional[str] = None) -> None:
    sub = subtitle or ""
    st.markdown(
        f"""
        <div class="saas-page-header">
          <div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(sub)}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_grid(items: List[Tuple[str, str, str, bool]]) -> None:
    """items: (label, value, delta_text, accent_border)."""
    cards = []
    for label, value, delta, accent in items:
        ac = " accent" if accent else ""
        cards.append(
            f"""
            <div class="saas-kpi{ac}">
              <p class="label">{html.escape(label)}</p>
              <p class="value">{html.escape(value)}</p>
              <p class="delta">{html.escape(delta)}</p>
            </div>
            """
        )
    st.markdown(
        f'<div class="saas-kpi-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def panel_start(title: str) -> None:
    st.markdown(
        f'<div class="saas-panel"><p class="saas-panel-title">{html.escape(title)}</p>',
        unsafe_allow_html=True,
    )


def panel_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def ticket_row_html(
    ticket_id: str,
    title: str,
    hand: Optional[str],
    meta: str,
    priority: Optional[str] = None,
) -> str:
    pri = f'<span class="badge badge-pending">{html.escape(priority)}</span>' if priority else ""
    return f"""
    <div class="saas-ticket-row">
      <div>
        <p class="title">{html.escape(title)}</p>
        <p class="meta">{html.escape(meta)} · ID {html.escape(ticket_id[:8])}</p>
      </div>
      <div>{hand_badge_html(hand)} {pri}</div>
    </div>
    """


def auth_page_shell() -> None:
    """Invisible marker — CSS hides sidebar and centers sign-in."""
    st.markdown('<div class="auth-page-marker"></div>', unsafe_allow_html=True)


def auth_signin_card() -> None:
    """Single HTML block: Welcome to + logo + tagline (fixes empty white box)."""
    st.markdown(
        f"""
        <div class="auth-card">
          <p class="welcome-to">Welcome to</p>
          <p class="brand">{html.escape(PRODUCT_NAME)}<span class="dot">.</span></p>
          <p class="tagline">{html.escape(TAGLINE)}</p>
          <p class="caption">{html.escape(PRODUCT_ABBREVIATION)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def auth_picker_intro() -> None:
    st.markdown(
        """
        <div class="auth-picker-box">
          <h3>Sign in</h3>
          <p>Search and select your account.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_name_from_email(email: str) -> str:
    local = email.split("@")[0]
    return local.replace(".", " ").replace("_", " ").title()


def hello_bar(email: str, role: str) -> None:
    name = display_name_from_email(email)
    role_label = ROLE_DISPLAY.get(role, role.title())
    st.markdown(
        f"""
        <div class="hello-bar">
          <h2>Hello, {html.escape(name)}</h2>
          <p>{html.escape(role_label)} · {html.escape(email)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confidence_label(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if value >= 0.8:
        return "Strong"
    if value >= 0.6:
        return "Good"
    return "Low"


def empty_state(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="saas-panel" style="text-align:center;padding:3rem;">
          <h3 style="margin:0 0 0.5rem;color:#0f172a;">{html.escape(title)}</h3>
          <p style="color:#64748b;margin:0;">{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
