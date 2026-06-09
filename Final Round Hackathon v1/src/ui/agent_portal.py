"""ITSM Agent Workspace — department queue triage & SLA dashboard."""
from __future__ import annotations

import html
import json
from typing import Optional

import streamlit as st

from src.config.brand import HAND_DISPLAY
from src.db.models import (
    AuditLog,
    ClassificationArtifact,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.stores.ticket_store import TicketStore
from src.ui import components as ui
from src.ui.agent_portal_theme import agent_portal_css
from src.ui.comments_ui import render_ticket_comments
from src.ui.ticket_display import (
    assignee_name,
    chip_html,
    dept_chip_class,
    department_label,
    hand_chip_class,
    hand_routing_label,
    person_name,
)

_AGENT_DISPLAY_NAMES = {
    "hardware@demo.local": "Alex Chen",
    "software@demo.local": "Marcus Lee",
    "secops@demo.local": "Sam Ortiz",
    "network@demo.local": "Priya Nair",
    "identity@demo.local": "Jordan Kim",
    "dba@demo.local": "Riley Park",
    "storage@demo.local": "Casey Morgan",
}

_REQUESTER_DISPLAY_NAMES = {
    "requester@demo.local": "Karan Joshi",
    "emily.reed@demo.local": "Emily Reed",
    "james.wu@demo.local": "James Wu",
    "sarah.kim@demo.local": "Sarah Kim",
    "michael.brown@demo.local": "Michael Brown",
}

_DEPT_ICONS = {
    "Hardware": "🖥️",
    "Software": "💻",
    "SecOps": "🛡️",
    "Network": "🌐",
    "Identity": "🔐",
    "DBA": "🗄️",
    "Storage": "💾",
}

_QUEUE_COLS = [0.72, 2.05, 0.48, 0.62, 0.78, 0.62, 0.82, 1.15]
_RESOLVED_COLS = [0.8, 2.4, 0.85, 0.95, 0.7, 0.75]
_FILTER_OPTIONS = ["All", "Unassigned", "Mine", "SLA at risk"]


def _display_name(email: str) -> str:
    if email in _AGENT_DISPLAY_NAMES:
        return _AGENT_DISPLAY_NAMES[email]
    if email in _REQUESTER_DISPLAY_NAMES:
        return _REQUESTER_DISPLAY_NAMES[email]
    local = email.split("@")[0]
    return local.replace(".", " ").replace("_", " ").title()


def _wrap(inner: str) -> str:
    return f'<div class="premium-agent-scope">{inner}</div>'


def _portal_scope_open() -> None:
    st.markdown(agent_portal_css(), unsafe_allow_html=True)
    st.markdown(
        '<div class="premium-agent-scope premium-scope-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def _ticket_key(ticket: Ticket) -> str:
    return ticket.ticket_id[:8].upper()


def _status_chip_class(status: str) -> str:
    mapping = {
        "ROUTED": "portal-chip portal-chip-status-info",
        "IN_PROGRESS": "portal-chip portal-chip-status-info",
        "HUMAN_REVIEW": "portal-chip portal-chip-status-warn",
        "ESCALATED": "portal-chip portal-chip-status-warn",
        "RESOLVED": "portal-chip portal-chip-status",
    }
    return mapping.get(status, "portal-chip portal-chip-status")


def _status_short_label(status: str) -> str:
    labels = {
        "ROUTED": "Open",
        "IN_PROGRESS": "In progress",
        "HUMAN_REVIEW": "Specialist review",
        "ESCALATED": "Needs specialist",
        "RESOLVED": "Closed",
        "RECEIVED": "New",
        "SELF_HELP": "Self-help",
    }
    return labels.get(status, status.replace("_", " ").title())


def _hand_label(hand: str) -> str:
    if hand == "2":
        return "Team assist"
    if hand == "3":
        return "Specialist"
    return "—"


def _hand_chip_class(hand: str) -> str:
    if hand == "2":
        return "portal-chip portal-chip-hand-2"
    if hand == "3":
        return "portal-chip portal-chip-hand"
    return "portal-chip portal-chip-status"


def _priority_class(priority: str | None) -> str:
    p = (priority or "P2").upper()
    if p == "P0":
        return "portal-chip-priority pri-p0"
    if p == "P1":
        return "portal-chip-priority pri-p1"
    return "portal-chip-priority pri-p2"


def _assignee_label(ticket: Ticket, me: User, session) -> str:
    if not ticket.assignee_id:
        return "Unassigned"
    if ticket.assignee_id == me.user_id:
        return "You"
    return assignee_name(session, ticket)


def _assignee_html(ticket: Ticket, me: User, session) -> str:
    lbl = _assignee_label(ticket, me, session)
    cls = "assignee-you" if lbl == "You" else "assignee-open" if lbl == "Unassigned" else ""
    return f'<p class="portal-row-assignee {cls}">{html.escape(lbl)}</p>'


def _filter_tickets(tickets: list[Ticket], filt: str, me: User) -> list[Ticket]:
    if filt == "Unassigned":
        return [t for t in tickets if not t.assignee_id]
    if filt == "Mine":
        return [t for t in tickets if t.assignee_id == me.user_id]
    if filt == "SLA at risk":
        return [t for t in tickets if TicketStore.sla_at_risk(t)]
    return tickets


def _topnav_html() -> str:
    return _wrap(
        '<header class="portal-topnav">'
        '<p class="portal-brand">ClearHand.</p>'
        '<div class="portal-nav-actions">'
        '<span class="portal-nav-hint">Agent Workspace</span>'
        "</div></header>"
    )


def _render_topnav(signout_key: str = "agent_signout") -> None:
    st.markdown(_topnav_html(), unsafe_allow_html=True)
    if st.button("Sign out", key=signout_key):
        _sign_out()


def _profile_card_html(name: str, email: str, department: str) -> str:
    return _wrap(
        '<div class="portal-profile-card">'
        f'<div class="portal-avatar">{_DEPT_ICONS.get(department, "🛠️")}</div>'
        f'<p class="portal-welcome">Welcome, {html.escape(name)}</p>'
        f'<p class="portal-email">{html.escape(email)}</p>'
        f'<span class="agent-dept-badge">{html.escape(department)} Queue</span>'
        '<p class="portal-org">ClearHand Support Operations</p>'
        "</div>"
    )


def _queue_summary_html(department: str, total: int, mine: int) -> str:
    return _wrap(
        '<div class="agent-queue-card">'
        '<p class="agent-queue-lbl">Department queue</p>'
        f'<p class="agent-queue-dept">{html.escape(department)}</p>'
        f'<p class="agent-queue-val">{total}</p>'
        f'<p class="agent-queue-sub">active incident{"s" if total != 1 else ""}</p>'
        f'<p class="agent-queue-mine">{mine} assigned to you</p>'
        "</div>"
    )


def _metrics_html(stats: dict) -> str:
    unassigned = stats["unassigned"]
    mine = stats["mine"]
    at_risk = stats["at_risk"]
    escalations = stats["escalations"]
    return _wrap(
        '<div class="portal-dash">'
        '<p class="portal-dash-heading">Team dashboard</p>'
        '<div class="portal-metrics">'
        '<div class="portal-metric portal-metric-unassigned">'
        '<div class="portal-metric-icon portal-metric-icon-unassigned">📥</div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{unassigned}</p>'
        '<p class="portal-metric-lbl">Unassigned</p>'
        '<p class="portal-metric-hint">Needs owner</p></div></div>'
        '<div class="portal-metric portal-metric-mine">'
        '<div class="portal-metric-icon portal-metric-icon-mine">👤</div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{mine}</p>'
        '<p class="portal-metric-lbl">Assigned to me</p>'
        '<p class="portal-metric-hint">Your active work</p></div></div>'
        '<div class="portal-metric portal-metric-risk">'
        '<div class="portal-metric-icon portal-metric-icon-risk">⏱</div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{at_risk}</p>'
        '<p class="portal-metric-lbl">SLA at risk</p>'
        '<p class="portal-metric-hint">Act soon</p></div></div>'
        '<div class="portal-metric portal-metric-escalation">'
        '<div class="portal-metric-icon portal-metric-icon-escalation">⚠️</div>'
        '<div class="portal-metric-body">'
        f'<p class="portal-metric-val">{escalations}</p>'
        '<p class="portal-metric-lbl">Specialist queue</p>'
        '<p class="portal-metric-hint">Needs expert review</p></div></div>'
        "</div></div>"
    )


def _queue_header_html() -> str:
    return _wrap(
        '<div class="portal-queue-head">'
        "<span>ID</span><span>Summary</span><span>Pri</span><span>SLA</span>"
        "<span>Department</span><span>Routing</span><span>Assignee</span><span>Actions</span>"
        "</div>"
    )


def _resolved_header_html() -> str:
    return _wrap(
        '<div class="portal-queue-head portal-queue-head-resolved">'
        "<span>ID</span><span>Summary</span><span>Closed</span>"
        "<span>Department</span><span>Routing</span><span></span>"
        "</div>"
    )


def _empty_state_html() -> str:
    return _wrap(
        '<div class="portal-empty-state">'
        '<p class="portal-empty-icon">✅</p>'
        '<p class="portal-empty-title">Queue clear</p>'
        '<p class="portal-empty-sub">No tickets match this filter in your department.</p>'
        "</div>"
    )


def _sign_out() -> None:
    dark = st.session_state.get("dark_mode", False)
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["signed_in"] = False
    st.session_state["dark_mode"] = dark
    st.rerun()


def _open_ticket(ticket_id: str) -> None:
    st.session_state["agent_view"] = "detail"
    st.session_state["ticket_id"] = ticket_id
    st.session_state["page"] = "agent"
    st.rerun()


def _assign_ticket(session, ticket: Ticket, user: User) -> None:
    TicketStore(session).assign(ticket, user)
    st.session_state["agent_flash"] = f"INC-{_ticket_key(ticket)} assigned to you."
    st.session_state["agent_flash_type"] = "success"
    st.rerun()


def _release_ticket(session, ticket: Ticket) -> None:
    TicketStore(session).release(ticket)
    st.session_state["agent_flash"] = f"INC-{_ticket_key(ticket)} released to queue."
    st.session_state["agent_flash_type"] = "info"
    st.rerun()


def _resolve_ticket(session, ticket: Ticket) -> None:
    TicketStore(session).resolve(ticket)
    st.session_state["agent_flash"] = f"INC-{_ticket_key(ticket)} marked resolved."
    st.session_state["agent_flash_type"] = "success"
    st.session_state["agent_view"] = "home"
    st.rerun()


def _similar_tickets(session, ticket: Ticket, clf: ClassificationArtifact | None) -> list[Ticket]:
    if not clf:
        return []
    return (
        session.query(Ticket)
        .join(ClassificationArtifact, ClassificationArtifact.ticket_id == Ticket.ticket_id)
        .filter(
            Ticket.department_queue == ticket.department_queue,
            Ticket.status == "RESOLVED",
            Ticket.ticket_id != ticket.ticket_id,
            ClassificationArtifact.use_case_category == clf.use_case_category,
        )
        .order_by(Ticket.created_at.desc())
        .limit(3)
        .all()
    )


def _render_queue_rows(
    tickets: list[Ticket],
    user: User,
    session,
    prefix: str,
) -> None:
    if not tickets:
        st.markdown(_empty_state_html(), unsafe_allow_html=True)
        return

    st.markdown(_queue_header_html(), unsafe_allow_html=True)
    store = TicketStore(session)

    for t in tickets:
        inc_key = _ticket_key(t)
        title_short = t.title if len(t.title) <= 44 else t.title[:41] + "…"
        requester = session.get(User, t.user_id)
        req_lbl = _display_name(requester.email) if requester else "Unknown"
        sla_txt, sla_cls = store.sla_label(t)
        dept_lbl = department_label(t)
        hand_lbl = hand_routing_label(t)
        pri_cls = _priority_class(t.priority)
        owner_html = _assignee_html(t, user, session)

        (
            c_id,
            c_sum,
            c_pri,
            c_sla,
            c_stat,
            c_hand,
            c_own,
            c_act,
        ) = st.columns(_QUEUE_COLS, gap="small")

        with c_id:
            st.markdown(
                _wrap(f'<p class="portal-row-id">INC-{html.escape(inc_key)}</p>'),
                unsafe_allow_html=True,
            )
        with c_sum:
            st.markdown(
                _wrap(
                    f'<p class="portal-row-title">{html.escape(title_short)}</p>'
                    f'<p class="portal-row-sub">{html.escape(req_lbl)}</p>'
                ),
                unsafe_allow_html=True,
            )
        with c_pri:
            st.markdown(
                _wrap(
                    f'<span class="{pri_cls}">{html.escape(t.priority or "P2")}</span>'
                ),
                unsafe_allow_html=True,
            )
        with c_sla:
            st.markdown(
                _wrap(f'<p class="portal-row-sla {sla_cls}">{html.escape(sla_txt)}</p>'),
                unsafe_allow_html=True,
            )
        with c_stat:
            st.markdown(
                _wrap(chip_html(dept_chip_class(t), dept_lbl)),
                unsafe_allow_html=True,
            )
        with c_hand:
            st.markdown(
                _wrap(chip_html(hand_chip_class(t.hand or ""), hand_lbl)),
                unsafe_allow_html=True,
            )
        with c_own:
            st.markdown(_wrap(owner_html), unsafe_allow_html=True)
        with c_act:
            if st.button("View", key=f"agent_view_{prefix}_{t.ticket_id}", type="secondary"):
                _open_ticket(t.ticket_id)
            if prefix == "inbox":
                if not t.assignee_id:
                    if st.button("Take", key=f"agent_assign_{prefix}_{t.ticket_id}", type="primary"):
                        _assign_ticket(session, t, user)
                elif t.assignee_id == user.user_id:
                    if st.button("Drop", key=f"agent_drop_{prefix}_{t.ticket_id}", type="tertiary"):
                        _release_ticket(session, t)


def _render_resolved_rows(
    tickets: list[Ticket],
    user: User,
    session,
    prefix: str,
) -> None:
    if not tickets:
        st.caption("No closed tickets yet.")
        return

    st.markdown(_resolved_header_html(), unsafe_allow_html=True)
    for t in tickets:
        inc_key = _ticket_key(t)
        title_short = t.title if len(t.title) <= 48 else t.title[:45] + "…"
        requester = session.get(User, t.user_id)
        req_lbl = person_name(requester.email) if requester else "Unknown"
        closed = t.updated_at.strftime("%b %d, %Y") if t.updated_at else "—"
        dept_lbl = department_label(t)
        hand_lbl = hand_routing_label(t)

        c_id, c_sum, c_closed, c_dept, c_route, c_view = st.columns(_RESOLVED_COLS, gap="small")
        with c_id:
            st.markdown(
                _wrap(f'<p class="portal-row-id">INC-{html.escape(inc_key)}</p>'),
                unsafe_allow_html=True,
            )
        with c_sum:
            st.markdown(
                _wrap(
                    f'<p class="portal-row-title">{html.escape(title_short)}</p>'
                    f'<p class="portal-row-sub">{html.escape(req_lbl)}</p>'
                ),
                unsafe_allow_html=True,
            )
        with c_closed:
            st.markdown(
                _wrap(f'<p class="portal-row-sub">{html.escape(closed)}</p>'),
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
        with c_view:
            if st.button("View", key=f"agent_view_{prefix}_{t.ticket_id}", type="secondary"):
                _open_ticket(t.ticket_id)


def render_agent_home(user: User, session) -> None:
    dept = user.department or "Hardware"
    name = _display_name(user.email)
    store = TicketStore(session)
    stats = store.department_stats(dept, user.user_id)

    flash = st.session_state.pop("agent_flash", None)
    flash_type = st.session_state.pop("agent_flash_type", "success")

    _render_topnav("agent_signout")

    top_col1, top_col2 = st.columns([1, 1.4], gap="large")
    with top_col1:
        st.markdown(_profile_card_html(name, user.email, dept), unsafe_allow_html=True)
    with top_col2:
        st.markdown(
            _queue_summary_html(dept, stats["total"], stats["mine"]),
            unsafe_allow_html=True,
        )

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown(_metrics_html(stats), unsafe_allow_html=True)

    if flash:
        cls = "itsm-banner-ok" if flash_type == "success" else "itsm-banner-info"
        st.markdown(
            _wrap(f'<div class="itsm-banner {cls}">{html.escape(flash)}</div>'),
            unsafe_allow_html=True,
        )

    filt = st.session_state.get("agent_filter", "All")
    st.markdown(
        _wrap('<p class="agent-filter-lbl">Queue filter</p>'),
        unsafe_allow_html=True,
    )
    selected = st.radio(
        "Queue filter",
        _FILTER_OPTIONS,
        index=_FILTER_OPTIONS.index(filt) if filt in _FILTER_OPTIONS else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="agent_filter_radio",
    )
    st.session_state["agent_filter"] = selected

    filtered = _filter_tickets(stats["tickets"], selected, user)

    with st.expander(f"Department inbox ({len(filtered)})", expanded=True):
        _render_queue_rows(filtered, user, session, "inbox")

    resolved = [
        t
        for t in store.list_for_department(dept, include_resolved=True)
        if t.status == "RESOLVED"
    ]
    if resolved:
        with st.expander(f"Recently closed ({len(resolved)})", expanded=False):
            _render_resolved_rows(resolved[:8], user, session, "resolved")


def render_agent_detail(user: User, session, ticket_id: Optional[str]) -> None:
    if not ticket_id:
        st.warning("Select a ticket first.")
        return

    ticket = TicketStore(session).get(ticket_id)
    dept = user.department or "Hardware"
    if not ticket or ticket.department_queue != dept:
        st.error("Ticket not found or not in your department queue.")
        return
    if ticket.hand not in ("2", "3"):
        st.error("This ticket is not in the assignee queue.")
        return

    clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket_id).first()
    res = session.query(ResolutionArtifact).filter_by(ticket_id=ticket_id).first()
    audits = (
        session.query(AuditLog)
        .filter_by(ticket_id=ticket_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    requester = session.get(User, ticket.user_id)
    req_name = _display_name(requester.email) if requester else "Unknown"
    hand_label, _, _ = HAND_DISPLAY.get(ticket.hand or "2", ("Team Assist", "", ""))
    confidence = ui.confidence_label(ticket.confidence)
    sla_txt, sla_cls = TicketStore(session).sla_label(ticket)
    key = _ticket_key(ticket)
    similar = _similar_tickets(session, ticket, clf)

    _render_topnav("agent_signout_detail")

    if st.button("← Back to dashboard", key="agent_detail_back", type="tertiary"):
        st.session_state["agent_view"] = "home"
        st.session_state["page"] = "agent"
        st.rerun()

    banner_cls = "itsm-banner-warn" if ticket.hand == "3" else "itsm-banner-info"
    banner_head = (
        "Human escalation — specialist review required"
        if ticket.hand == "3"
        else f"Routed assist — {dept} queue"
    )
    banner_body = (
        "This incident needs specialist review. Check audit context before acting."
        if ticket.hand == "3"
        else "AI suggested resolution available below. Validate before closing with requester."
    )

    owner_lbl = _assignee_label(ticket, user, session)

    st.markdown(
        _wrap(
            f'<div class="itsm-record">'
            f'<div class="itsm-record-top">'
            f'<p class="itsm-record-key">INC-{html.escape(key)}</p>'
            f'<h2 class="itsm-record-title">{html.escape(ticket.title)}</h2>'
            f'<div class="itsm-state-bar">'
            f'<span class="itsm-chip itsm-chip-status">'
            f'{html.escape(_status_short_label(ticket.status))}</span>'
            f'<span class="itsm-chip itsm-chip-domain">{html.escape(dept)}</span>'
            f'<span class="itsm-chip itsm-chip-hand-2">'
            f'{html.escape(hand_routing_label(ticket))}</span>'
            f"</div></div>"
            f'<div class="itsm-banner {banner_cls}">'
            f"<strong>{html.escape(banner_head)}</strong><br>{html.escape(banner_body)}</div>"
            f'<div class="itsm-meta-grid">'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Requester</p>'
            f'<p class="itsm-meta-val">{html.escape(req_name)}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Department</p>'
            f'<p class="itsm-meta-val">{html.escape(department_label(ticket))}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Routing</p>'
            f'<p class="itsm-meta-val">{html.escape(hand_routing_label(ticket))}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Assignee</p>'
            f'<p class="itsm-meta-val">{html.escape(owner_lbl)}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Match strength</p>'
            f'<p class="itsm-meta-val">{html.escape(confidence)}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Priority</p>'
            f'<p class="itsm-meta-val">{html.escape(ticket.priority or "—")}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">SLA</p>'
            f'<p class="itsm-meta-val {sla_cls}">{html.escape(sla_txt)}</p></div>'
            f'<div class="itsm-meta-cell"><p class="itsm-meta-lbl">Urgency</p>'
            f'<p class="itsm-meta-val">{html.escape(ticket.urgency.title())}</p></div>'
            f"</div></div>"
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _wrap(
            f'<div class="itsm-section"><p class="itsm-section-title">Incident description</p>'
            f'<p style="margin:0;color:#475569;font-size:0.9rem;line-height:1.55;">'
            f"{html.escape(ticket.description_sanitized or ticket.description_raw)}"
            f"</p></div>"
        ),
        unsafe_allow_html=True,
    )

    if clf:
        st.markdown(
            _wrap(
                f'<div class="itsm-section"><p class="itsm-section-title">Classification</p>'
                f'<p class="itsm-meta-val">{html.escape(clf.use_case_category)}'
                f"{f' · {html.escape(clf.subcategory)}' if clf.subcategory else ''}"
                f"</p></div>"
            ),
            unsafe_allow_html=True,
        )

    if res and ticket.hand == "2":
        steps = json.loads(res.steps_json or "[]")
        cites = json.loads(res.citations_json or "[]")
        if steps:
            step_items = "".join(
                f"<li style='margin-bottom:0.35rem;'>{html.escape(s)}</li>" for s in steps
            )
            cite_items = "".join(
                f"<li style='margin-bottom:0.25rem;'>{html.escape(c)}</li>" for c in cites
            )
            st.markdown(
                _wrap(
                    f'<div class="itsm-section"><p class="itsm-section-title">'
                    f"AI suggested resolution</p>"
                    f"<ol style='margin:0 0 0.75rem;padding-left:1.2rem;color:#475569;"
                    f"font-size:0.9rem;'>{step_items}</ol>"
                    f"<p class='itsm-section-title'>References</p>"
                    f"<ul style='margin:0;padding-left:1.2rem;color:#64748B;"
                    f"font-size:0.85rem;'>{cite_items}</ul></div>"
                ),
                unsafe_allow_html=True,
            )

    if similar:
        sim_items = "".join(
            f"<li style='margin-bottom:0.3rem;'>INC-{_ticket_key(s)} — "
            f"{html.escape(s.title[:48])}</li>"
            for s in similar
        )
        st.markdown(
            _wrap(
                f'<div class="itsm-section"><p class="itsm-section-title">'
                f"Similar resolved tickets</p>"
                f"<ul style='margin:0;padding-left:1.2rem;color:#475569;"
                f"font-size:0.88rem;'>{sim_items}</ul></div>"
            ),
            unsafe_allow_html=True,
        )

    if ticket.hand == "3" or res and res.low_grounding:
        audit_lines = "".join(
            f"<li style='margin-bottom:0.25rem;font-size:0.82rem;color:#64748B;'>"
            f"{a.timestamp:%H:%M:%S} — {html.escape(a.agent or 'system')}: "
            f"{html.escape(a.event_type)}</li>"
            for a in audits[:8]
        )
        st.markdown(
            _wrap(
                f'<div class="itsm-section"><p class="itsm-section-title">Audit context</p>'
                f"<ul style='margin:0;padding-left:1.1rem;'>{audit_lines}</ul></div>"
            ),
            unsafe_allow_html=True,
        )

    st.markdown(_wrap('<p class="itsm-section-title">Actions</p>'), unsafe_allow_html=True)
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if not ticket.assignee_id:
            if st.button("Assign to me", key="agent_detail_assign", type="primary", use_container_width=True):
                _assign_ticket(session, ticket, user)
        elif ticket.assignee_id == user.user_id:
            if st.button("Release to queue", key="agent_detail_release", use_container_width=True):
                _release_ticket(session, ticket)
        else:
            st.caption(f"Owned by {_assignee_label(ticket, user, session)}")
    with ac2:
        if ticket.status != "RESOLVED":
            if st.button("Mark resolved", key="agent_detail_resolve", type="primary", use_container_width=True):
                _resolve_ticket(session, ticket)
    with ac3:
        if st.button("Back to inbox", key="agent_detail_inbox", use_container_width=True):
            st.session_state["agent_view"] = "home"
            st.rerun()

    render_ticket_comments(session, ticket_id, user, _wrap, "agent")


def render_agent_portal(user: User, session) -> None:
    _portal_scope_open()
    if "agent_view" not in st.session_state:
        st.session_state["agent_view"] = "home"

    view = st.session_state["agent_view"]
    if view == "detail":
        render_agent_detail(user, session, st.session_state.get("ticket_id"))
    else:
        render_agent_home(user, session)
