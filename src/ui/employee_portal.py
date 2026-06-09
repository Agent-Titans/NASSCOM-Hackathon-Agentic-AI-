"""ITSM Employee Workspace — Jira / ServiceNow inspired, user-isolated tickets."""
from __future__ import annotations

import html
import json
from typing import Optional

import streamlit as st

from src.config.brand import HAND_DISPLAY, ORG_NAME, PRODUCT_NAME
from src.config.demo_profiles import demo_person_name
from src.db.models import ClassificationArtifact, Feedback, ResolutionArtifact, Ticket, User
from src.services.resolution_steps_codec import decode_steps
from src.services.ticket_service import TicketService
from src.stores.audit_store import AuditLogStore
from src.stores.ticket_store import TicketStore
from src.ui import components as ui
from src.ui.comments_ui import render_ticket_comments
from src.ui.employee_portal_theme import employee_portal_css
from src.ui.ticket_display import (
    assignee_name,
    chip_html,
    dept_chip_class,
    department_label,
    hand_chip_class,
    hand_routing_label,
)


def _sync_auth_user(user: User) -> None:
    st.session_state["auth_user"] = user.email
    st.session_state["auth_user_id"] = user.user_id


_PRIORITY_OPTIONS: tuple[str, ...] = ("P0", "P1", "P2")

_PRIORITY_TO_URGENCY: dict[str, str] = {
    "P0": "high",
    "P1": "medium",
    "P2": "low",
}


def _display_name(email: str) -> str:
    return demo_person_name(email)


def _user_tickets(session, user: User) -> list[Ticket]:
    auth_email = st.session_state.get("auth_user", user.email)
    auth_user_id = st.session_state.get("auth_user_id", user.user_id)
    if auth_email != user.email or auth_user_id != user.user_id:
        auth_email = user.email
        auth_user_id = user.user_id
        st.session_state["auth_user"] = auth_email
        st.session_state["auth_user_id"] = auth_user_id
    return (
        session.query(Ticket)
        .join(User, Ticket.user_id == User.user_id)
        .filter(User.email == auth_email)
        .filter(Ticket.user_id == auth_user_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )


def _split_ticket_sets(user_tickets: list[Ticket]) -> tuple[list[Ticket], list[Ticket]]:
    pending = [t for t in user_tickets if t.status != "RESOLVED"]
    past = [t for t in user_tickets if t.status == "RESOLVED"]
    return pending, past


def _ticket_key(ticket: Ticket) -> str:
    return ticket.ticket_id[:8].upper()


def _status_label(ticket: Ticket) -> str:
    return ticket.status.replace("_", " ").title()


def _status_chip_class(status: str) -> str:
    mapping = {
        "SELF_HELP": "portal-chip portal-chip-status-ok",
        "ROUTED": "portal-chip portal-chip-status-info",
        "IN_PROGRESS": "portal-chip portal-chip-status-info",
        "HUMAN_REVIEW": "portal-chip portal-chip-status-warn",
        "ESCALATED": "portal-chip portal-chip-status-warn",
        "RECEIVED": "portal-chip portal-chip-status",
        "RESOLVED": "portal-chip portal-chip-status",
    }
    return mapping.get(status, "portal-chip portal-chip-status")


def _status_short_label(status: str) -> str:
    labels = {
        "RECEIVED": "Submitted",
        "SELF_HELP": "Self-help",
        "ROUTED": "With team",
        "IN_PROGRESS": "In progress",
        "HUMAN_REVIEW": "With specialist",
        "ESCALATED": "With specialist",
        "RESOLVED": "Closed",
    }
    return labels.get(status, status.replace("_", " ").title())


_QUEUE_COLS = [0.8, 2.05, 0.95, 0.7, 1.05, 0.7]


def _hand_chip_class(hand: str) -> str:
    if hand == "1":
        return "portal-chip portal-chip-hand-1"
    if hand == "2":
        return "portal-chip portal-chip-hand-2"
    if hand == "3":
        return "portal-chip portal-chip-hand"
    return "portal-chip portal-chip-status"


def _hand_chip_label(ticket: Ticket) -> str:
    hand = ticket.hand or ""
    if hand == "1":
        return "Self-help"
    if hand == "2":
        return "Team assist"
    if hand == "3":
        return "Specialist"
    return "Routing"


def _routing_copy(ticket: Ticket) -> dict[str, str]:
    hand = ticket.hand or ""
    dept = ticket.department_queue or "—"
    if hand == "3":
        team = dept if dept != "—" else "Specialist Desk"
        return {
            "badge": "Human Verification",
            "headline": "Routed to human specialist",
            "body": (
                f"Under specialist review by the {team} team. "
                "A human agent will verify and resolve this request."
            ),
            "team": team,
            "status": _status_label(ticket),
            "banner_cls": "itsm-banner-warn",
        }
    if hand == "2":
        return {
            "badge": "Team Queue",
            "headline": f"Routed to {dept}",
            "body": (
                f"In the {dept} queue · Priority {ticket.priority or 'P2'} · "
                f"SLA {ticket.sla_hours or '—'}h."
            ),
            "team": dept,
            "status": _status_label(ticket),
            "banner_cls": "itsm-banner-info",
        }
    if hand == "1":
        return {
            "badge": "Self-Help",
            "headline": "Self-help guidance available",
            "body": "Follow the recommended steps below. Escalate if you still need help.",
            "team": "Self-Service",
            "status": _status_label(ticket),
            "banner_cls": "itsm-banner-ok",
        }
    return {
        "badge": "Processing",
        "headline": "Routing in progress",
        "body": "Your request is being classified and routed.",
        "team": "—",
        "status": _status_label(ticket),
        "banner_cls": "itsm-banner-info",
    }


def _portal_scope_open() -> None:
    st.markdown(employee_portal_css(), unsafe_allow_html=True)
    st.markdown(
        '<div class="premium-portal-scope premium-scope-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def _wrap(inner: str) -> str:
    return f'<div class="premium-portal-scope">{inner}</div>'


def _topnav_html() -> str:
    return _wrap(
        '<header class="portal-topnav">'
        f'<p class="portal-brand">{html.escape(PRODUCT_NAME)}.</p>'
        '<div class="portal-nav-actions" aria-hidden="true">'
        '<span class="portal-nav-hint">Employee Workspace</span>'
        "</div></header>"
    )


def _render_topnav(signout_key: str = "portal_signout") -> None:
    st.markdown(_topnav_html(), unsafe_allow_html=True)
    if st.button("Sign out", key=signout_key):
        _sign_out()


def _profile_card_html(name: str, email: str) -> str:
    return _wrap(
        '<div class="portal-profile-card">'
        '<div class="portal-avatar">👨‍💻</div>'
        f'<p class="portal-welcome">Welcome, {html.escape(name)}</p>'
        f'<p class="portal-email">{html.escape(email)}</p>'
        f'<p class="portal-org">{html.escape(ORG_NAME)} Core</p>'
        "</div>"
    )


def _action_card_html() -> str:
    return _wrap(
        '<div class="portal-action-bundle portal-action-card">'
        '<p class="portal-action-title">+ New Request</p>'
        '<p class="portal-action-desc">'
        "Submit a new operational incident to trigger autonomous AI agent routing tracks"
        "</p></div>"
    )


def _go_create_view() -> None:
    st.session_state["portal_view"] = "create"
    st.session_state["page"] = "portal"


def _empty_state_html() -> str:
    return _wrap(
        '<div class="portal-empty-state">'
        '<p class="portal-empty-icon">✨</p>'
        '<p class="portal-empty-title">All clear</p>'
        '<p class="portal-empty-sub">No open requests need operational triage right now.</p>'
        "</div>"
    )


def _metrics_html(open_count: int, resolved_count: int, total: int) -> str:
    open_hint = "Needs attention" if open_count else "All clear"
    return _wrap(
        '<div class="portal-dash">'
        '<p class="portal-dash-heading">Workspace overview</p>'
        '<div class="portal-metrics">'
        f'<div class="portal-metric portal-metric-open">'
        '<div class="portal-metric-icon portal-metric-icon-open" aria-hidden="true">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/>'
        '<path d="M12 7v5l3 2"/></svg></div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{open_count}</p>'
        '<p class="portal-metric-lbl">Open</p>'
        f'<p class="portal-metric-hint">{html.escape(open_hint)}</p>'
        "</div></div>"
        f'<div class="portal-metric portal-metric-resolved">'
        '<div class="portal-metric-icon portal-metric-icon-resolved" aria-hidden="true">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4"/>'
        '<circle cx="12" cy="12" r="9"/></svg></div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{resolved_count}</p>'
        '<p class="portal-metric-lbl">Resolved</p>'
        '<p class="portal-metric-hint">Completed</p>'
        "</div></div>"
        f'<div class="portal-metric portal-metric-total">'
        '<div class="portal-metric-icon portal-metric-icon-total" aria-hidden="true">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/>'
        '<path d="M8 12h8M12 8v8"/></svg></div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{total}</p>'
        '<p class="portal-metric-lbl">Total</p>'
        '<p class="portal-metric-hint">All requests</p>'
        "</div></div>"
        "</div></div>"
    )


def _queue_header_html() -> str:
    return _wrap(
        '<div class="portal-queue-head">'
        "<span>ID</span><span>Summary</span><span>Department</span>"
        "<span>Routing</span><span>Assignee</span><span></span>"
        "</div>"
    )


def _sign_out() -> None:
    dark = st.session_state.get("dark_mode", False)
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["signed_in"] = False
    st.session_state["dark_mode"] = dark
    st.rerun()


def _submit_feedback(session, ticket_id: str, outcome: str) -> None:
    session.add(Feedback(ticket_id=ticket_id, outcome=outcome))
    if outcome == "worked":
        ticket = TicketStore(session).get(ticket_id)
        if ticket:
            TicketStore(session).resolve(ticket)
            return
    session.commit()


def _escalate_ticket(session, ticket_id: str) -> None:
    """Hand 1 self-help failed → route to team assist (Hand 2), not specialist."""
    ticket = TicketStore(session).get(ticket_id)
    if not ticket:
        return
    TicketStore(session).update_hand(
        ticket,
        hand="2",
        confidence=ticket.confidence or 0.5,
        status="ROUTED",
        escalation_required=False,
    )
    AuditLogStore(session).record(
        ticket,
        "feedback_escalation",
        details="outcome=failed hand=1_to_2",
    )
    session.commit()


def _open_ticket(ticket_id: str) -> None:
    st.session_state["portal_view"] = "detail"
    st.session_state["ticket_id"] = ticket_id
    st.session_state["page"] = "portal"
    st.rerun()


def _render_ticket_list(tickets: list[Ticket], session, prefix: str) -> None:
    if not tickets:
        st.caption("No tickets in this queue.")
        return

    st.markdown(_queue_header_html(), unsafe_allow_html=True)
    for t in tickets:
        title_short = t.title if len(t.title) <= 48 else t.title[:45] + "…"
        inc_key = _ticket_key(t)
        dept_lbl = department_label(t)
        hand_lbl = hand_routing_label(t)
        owner_lbl = assignee_name(session, t)

        c_id, c_sum, c_dept, c_route, c_owner, c_view = st.columns(_QUEUE_COLS, gap="small")
        with c_id:
            st.markdown(
                _wrap(f'<p class="portal-row-id">INC-{html.escape(inc_key)}</p>'),
                unsafe_allow_html=True,
            )
        with c_sum:
            st.markdown(
                _wrap(f'<p class="portal-row-title">{html.escape(title_short)}</p>'),
                unsafe_allow_html=True,
            )
        with c_dept:
            st.markdown(
                _wrap(chip_html(dept_chip_class(t), dept_lbl)),
                unsafe_allow_html=True,
            )
        with c_route:
            st.markdown(
                _wrap(chip_html(hand_chip_class(t.hand or ""), hand_lbl)),
                unsafe_allow_html=True,
            )
        with c_owner:
            st.markdown(
                _wrap(f'<p class="portal-row-assignee">{html.escape(owner_lbl)}</p>'),
                unsafe_allow_html=True,
            )
        with c_view:
            if st.button("View", key=f"portal_view_{prefix}_{t.ticket_id}", type="secondary"):
                _open_ticket(t.ticket_id)


def render_portal_home(user: User, session) -> None:
    _sync_auth_user(user)
    user_tickets = _user_tickets(session, user)
    pending_tickets, past_tickets = _split_ticket_sets(user_tickets)
    pending_count = len(pending_tickets)
    resolved_count = len(past_tickets)

    flash = st.session_state.pop("portal_flash", None)
    flash_type = st.session_state.pop("portal_flash_type", "success")
    name = _display_name(user.email)
    auth_email = st.session_state.get("auth_user", user.email)

    _render_topnav("portal_signout")

    top_col1, top_col2 = st.columns([1, 1.4], gap="large")
    with top_col1:
        st.markdown(_profile_card_html(name, auth_email), unsafe_allow_html=True)
    with top_col2:
        st.markdown(_action_card_html(), unsafe_allow_html=True)
        st.button(
            "+ New Request",
            key="portal_btn_create",
            type="primary",
            use_container_width=True,
            on_click=_go_create_view,
        )

    st.markdown('<div style="margin-top: 2.5rem;"></div>', unsafe_allow_html=True)

    st.markdown(
        _metrics_html(pending_count, resolved_count, len(user_tickets)),
        unsafe_allow_html=True,
    )

    if flash:
        cls = "itsm-banner-ok" if flash_type == "success" else "itsm-banner-info"
        st.markdown(
            _wrap(f'<div class="itsm-banner {cls}">{html.escape(flash)}</div>'),
            unsafe_allow_html=True,
        )

    if pending_count > 0:
        with st.expander(f"My Open Requests ({pending_count})", expanded=False):
            _render_ticket_list(pending_tickets, session, "pending")
    else:
        st.markdown(_empty_state_html(), unsafe_allow_html=True)

    with st.expander(f"Closed requests ({resolved_count})", expanded=False):
        if past_tickets:
            _render_ticket_list(past_tickets, session, "hist")
        else:
            st.caption("No resolved tickets recorded yet.")


def render_portal_create(user: User, session) -> None:
    _sync_auth_user(user)

    if st.button("← Back to workspace", key="portal_back_home", type="tertiary"):
        st.session_state["portal_view"] = "home"
        st.session_state["page"] = "portal"
        st.rerun()

    _render_topnav("portal_signout_create")
    st.markdown(
        _wrap(
            '<div class="portal-create-hero">'
            '<p class="portal-create-kicker">New request</p>'
            '<p class="portal-create-title">Submit a support ticket</p>'
            '<p class="portal-create-sub">'
            "Describe the issue — our AI agents classify, route, and suggest next steps."
            "</p></div>"
        ),
        unsafe_allow_html=True,
    )

    with st.form("portal_create_form", border=False):
        title = st.text_input(
            "Issue Title",
            placeholder="e.g. Cannot connect to VPN",
        )

        description = st.text_area(
            "Description",
            height=140,
            placeholder=(
                "What happened? Include error messages, when it started, "
                "and anything you already tried."
            ),
        )

        contact_email = st.text_input(
            "Contact email",
            value=user.email,
            placeholder="you@company.com",
            help="We will use this email for updates on this request.",
        )

        priority = st.radio(
            "Priority",
            _PRIORITY_OPTIONS,
            index=1,
            horizontal=True,
        )

        submitted = st.form_submit_button("Submit request", type="primary", use_container_width=True)

    if not submitted:
        return
    if not title.strip() or not description.strip():
        st.error("Issue Title and Description are required.")
        return
    if not contact_email.strip() or "@" not in contact_email:
        st.error("A valid contact email is required.")
        return

    full_description = f"{description.strip()}\n\nContact email: {contact_email.strip()}"
    urgency = _PRIORITY_TO_URGENCY[priority]

    try:
        ticket = TicketStore(session).create(user, title.strip(), full_description, urgency)
        with st.spinner("Routing through Guardrail → Classify → Route → Resolve → Supervisor…"):
            result = TicketService(session).process_ticket(ticket)
        session.refresh(ticket)

        hand = result.decision.hand
        if hand == "3":
            dept = ticket.department_queue or "Specialist Desk"
            st.session_state["portal_flash"] = f"Routed to human verification · {dept} team."
            st.session_state["portal_flash_type"] = "human"
        elif hand == "2":
            dept = ticket.department_queue or "IT Support"
            hl, _, _ = HAND_DISPLAY[hand]
            st.session_state["portal_flash"] = f"Routed to {hl} · {dept} queue."
            st.session_state["portal_flash_type"] = "success"
        else:
            hl, _, _ = HAND_DISPLAY[hand]
            st.session_state["portal_flash"] = f"{hl} steps ready — open your ticket to view."
            st.session_state["portal_flash_type"] = "success"

        st.session_state["portal_view"] = "detail"
        st.session_state["ticket_id"] = ticket.ticket_id
        st.session_state["page"] = "portal"
        st.rerun()
    except Exception as exc:
        st.error(str(exc))


def render_portal_detail(user: User, session, ticket_id: Optional[str]) -> None:
    _sync_auth_user(user)
    if not ticket_id:
        st.warning("Select a ticket first.")
        return

    ticket = TicketStore(session).get(ticket_id)
    auth_user_id = st.session_state.get("auth_user_id", user.user_id)
    if not ticket or ticket.user_id != auth_user_id:
        st.error("Ticket not found or access denied.")
        return

    clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket_id).first()
    res = session.query(ResolutionArtifact).filter_by(ticket_id=ticket_id).first()
    route = _routing_copy(ticket)
    hand_label, _, _ = HAND_DISPLAY.get(ticket.hand or "", ("Pending", "", ""))
    confidence = ui.confidence_label(ticket.confidence)
    key = _ticket_key(ticket)
    hand_cls = _hand_chip_class(ticket.hand or "").replace("portal-chip", "itsm-chip")

    _render_topnav("portal_signout_detail")

    if st.button("← Back to workspace", key="portal_detail_back", type="tertiary"):
        st.session_state["portal_view"] = "home"
        st.session_state["page"] = "portal"
        st.rerun()

    st.markdown(
        _wrap(
            f'<div class="itsm-record">'
            f'<div class="itsm-record-top">'
            f'<p class="itsm-record-key">INC-{html.escape(key)}</p>'
            f'<h2 class="itsm-record-title">{html.escape(ticket.title)}</h2>'
            f'<div class="itsm-state-bar">'
            f'<span class="itsm-chip itsm-chip-status">{html.escape(route["status"])}</span>'
            f'<span class="itsm-chip itsm-chip-domain">{html.escape(route["badge"])}</span>'
            f'<span class="{hand_cls}">{html.escape(hand_routing_label(ticket))}</span>'
            f"</div></div>"
            f'<div class="itsm-banner {route["banner_cls"]}" style="margin:1rem 1.25rem;">'
            f"<strong>{html.escape(route['headline'])}</strong><br>"
            f"{html.escape(route['body'])}</div>"
            f'<div class="itsm-meta-grid">'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Match strength</p>'
            f'<p class="itsm-meta-val">{html.escape(confidence)}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Department</p>'
            f'<p class="itsm-meta-val">{html.escape(department_label(ticket))}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Routing</p>'
            f'<p class="itsm-meta-val">{html.escape(hand_routing_label(ticket))}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Assignee</p>'
            f'<p class="itsm-meta-val">{html.escape(assignee_name(session, ticket))}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Priority</p>'
            f'<p class="itsm-meta-val">{html.escape(ticket.priority or "—")}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">SLA target</p>'
            f'<p class="itsm-meta-val">'
            f'{html.escape(str(ticket.sla_hours) + "h" if ticket.sla_hours else "—")}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Urgency</p>'
            f'<p class="itsm-meta-val">{html.escape(ticket.urgency.title())}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Opened</p>'
            f'<p class="itsm-meta-val">'
            f'{ticket.created_at.strftime("%b %d, %Y %H:%M")}</p></div>'
            f"</div></div>"
        ),
        unsafe_allow_html=True,
    )

    if clf:
        st.markdown(
            _wrap(
                f'<div class="itsm-section"><p class="itsm-section-title">Classification</p>'
                f'<p class="itsm-meta-val" style="font-weight:500;color:#475569;">'
                f"{html.escape(clf.use_case_category)}</p></div>"
            ),
            unsafe_allow_html=True,
        )

    if ticket.hand == "3":
        st.markdown(
            _wrap(
                '<div class="itsm-banner itsm-banner-warn" style="margin:0 0 1rem;">'
                "<strong>Human verification required</strong> — "
                "No automated self-help steps. A specialist will review this incident."
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    elif ticket.hand == "1" and res:
        steps, _ = decode_steps(res.steps_json)
        if steps:
            step_items = "".join(f"<li style='margin-bottom:0.35rem;'>{html.escape(s)}</li>" for s in steps)
            st.markdown(
                _wrap(
                    f'<div class="itsm-section"><p class="itsm-section-title">Resolution steps</p>'
                    f"<ol style='margin:0;padding-left:1.2rem;color:#475569;font-size:0.9rem;'>"
                    f"{step_items}</ol></div>"
                ),
                unsafe_allow_html=True,
            )
        st.markdown(_wrap('<p class="itsm-section-title">Did this resolve your issue?</p>'), unsafe_allow_html=True)
        fb1, fb2 = st.columns(2)
        with fb1:
            if st.button("Worked", key=f"portal_fb_worked_{ticket_id}", type="primary", use_container_width=True):
                _submit_feedback(session, ticket_id, "worked")
                st.session_state["portal_flash"] = "Thank you — your request is now closed."
                st.session_state["portal_flash_type"] = "success"
                st.session_state["portal_view"] = "home"
                st.rerun()
        with fb2:
            if st.button("Did not work", key=f"portal_fb_failed_{ticket_id}", use_container_width=True):
                _submit_feedback(session, ticket_id, "failed")
                _escalate_ticket(session, ticket_id)
                st.session_state["portal_flash"] = "Routed to your team queue for follow-up."
                st.session_state["portal_flash_type"] = "human"
                st.session_state["portal_view"] = "home"
                st.rerun()

    render_ticket_comments(session, ticket_id, user, _wrap, "portal")


def render_employee_portal(user: User, session) -> None:
    _portal_scope_open()
    if "portal_view" not in st.session_state:
        st.session_state["portal_view"] = "home"

    view = st.session_state["portal_view"]
    if view == "create":
        render_portal_create(user, session)
    elif view == "detail":
        render_portal_detail(user, session, st.session_state.get("ticket_id"))
    else:
        st.session_state["portal_view"] = "home"
        render_portal_home(user, session)
