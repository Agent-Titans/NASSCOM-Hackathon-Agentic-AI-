"""
Agent workspace — department queue triage, ticket detail, assign/resolve/route.

Views:
  home   — profile card, open queue, history, queue filter (open/assigned/resolved)
  detail — record header, expanders (description, routing context, resolution), Actions

Routing Specialists desk (SecOps only):
  _render_department_route_panel() — selectbox + Route for misroute correction.
  Regular agents see Route → specialists dialog; SecOps sees dept dropdown on H3 tickets.
"""
from __future__ import annotations

import html
import json
from typing import Optional

import streamlit as st

from src.config.brand import HAND_DISPLAY, ORG_NAME, PRODUCT_NAME
from src.config.departments import (
    OPERATIONAL_DEPARTMENT_QUEUES,
    departments_match,
    display_department,
)
from src.config.demo_profiles import demo_person_name
from src.config.specialists import (
    MIN_REASON_CHARS,
    SPECIALISTS_DISPLAY,
    SPECIALISTS_QUEUE,
    STATUS_ROUTING_REVIEW,
)
from src.services.reference_ticket_loader import (
    is_reference_seed_id,
    load_reference_ticket,
    normalize_reference_ticket_id,
)
from src.services.resolution_steps_codec import decode_steps
from src.services.specialists_desk_service import (
    can_request_specialist,
    get_specialist_context,
    is_specialists_ticket,
    keep_specialist_ticket_in_secops,
    list_specialists_history,
    list_specialists_queue,
    request_specialist_review,
    reroute_from_specialists,
    reroute_secops_operational,
)
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket, User
from src.stores.artifact_store import ArtifactStore
from src.stores.ticket_store import TicketStore
from src.ui import components as ui
from src.ui.agent_portal_theme import agent_portal_css
from src.ui.scroll_top import inject_scroll_to_top
from src.ui.citation_refs import render_resolution_references
from src.ui.comments_ui import render_ticket_comments
from src.ui.ticket_display import (
    assignee_name,
    chip_html,
    dept_chip_class,
    department_label,
    hand_chip_class,
    hand_routing_label,
    is_corpus_ticket_id,
    person_name,
)

_DEPT_ICONS = {
    "Infrastructure": "🖥️",
    "Hardware": "🖥️",
    "Application": "💻",
    "Software": "💻",
    "SecOps": "🛡️",
    "Network": "🌐",
    "Access Management": "🔐",
    "Identity": "🔐",
    "Database": "🗄️",
    "DBA": "🗄️",
    "Storage": "💾",
}

_QUEUE_COLS = [0.72, 2.05, 0.48, 0.62, 0.78, 0.62, 0.82, 1.15]
_RESOLVED_COLS = [0.8, 2.4, 0.85, 0.95, 0.7, 0.75]
_FILTER_OPTIONS = ["All", "Unassigned", "Mine", "SLA at risk"]
_AGENT_URL_VIEW = "agent_view"
_AGENT_URL_TICKET = "ticket"


def _restore_agent_state_from_url() -> None:
    """Keep assignee on the same screen after browser refresh."""
    try:
        qp = st.query_params
        view = qp.get(_AGENT_URL_VIEW)
        ticket = qp.get(_AGENT_URL_TICKET)
        if view in ("home", "detail"):
            st.session_state["agent_view"] = view
        if ticket:
            st.session_state["ticket_id"] = ticket
    except Exception:
        pass


def _sync_agent_url() -> None:
    try:
        view = st.session_state.get("agent_view", "home")
        st.query_params[_AGENT_URL_VIEW] = view
        tid = st.session_state.get("ticket_id")
        if view == "detail" and tid:
            st.query_params[_AGENT_URL_TICKET] = tid
        elif _AGENT_URL_TICKET in st.query_params:
            del st.query_params[_AGENT_URL_TICKET]
    except Exception:
        pass


def _go_agent_home() -> None:
    st.session_state.pop("agent_return_ticket_id", None)
    st.session_state.pop("agent_reference_view", None)
    st.session_state.pop("agent_route_dialog_ticket", None)
    st.session_state["agent_view"] = "home"
    st.session_state.pop("ticket_id", None)
    st.session_state["page"] = "agent"
    _sync_agent_url()


def _go_agent_detail(ticket_id: str) -> None:
    st.session_state.pop("agent_return_ticket_id", None)
    st.session_state.pop("agent_reference_view", None)
    st.session_state["agent_view"] = "detail"
    st.session_state["ticket_id"] = ticket_id
    st.session_state["page"] = "agent"
    _sync_agent_url()


def _user_can_act_on_ticket(ticket: Ticket, user: User) -> bool:
    """Agents may act only on unassigned tickets or tickets they own."""
    if ticket.status in ("RESOLVED", "CLOSED"):
        return False
    if not ticket.assignee_id:
        return True
    return ticket.assignee_id == user.user_id


def _ticket_owned_by_other(ticket: Ticket, user: User) -> bool:
    return bool(ticket.assignee_id and ticket.assignee_id != user.user_id)


def _display_name(email: str) -> str:
    return demo_person_name(email)


def _wrap(inner: str) -> str:
    return f'<div class="premium-agent-scope">{inner}</div>'


def _portal_scope_open() -> None:
    st.markdown(agent_portal_css(), unsafe_allow_html=True)
    st.markdown(
        '<div class="premium-agent-scope premium-scope-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    inject_scroll_to_top()


def _ticket_key(ticket: Ticket) -> str:
    return ticket.ticket_id[:8].upper()


def _status_chip_class(status: str) -> str:
    mapping = {
        "ROUTED": "portal-chip portal-chip-status-info",
        "IN_PROGRESS": "portal-chip portal-chip-status-info",
        "HUMAN_REVIEW": "portal-chip portal-chip-status-warn",
        "ESCALATED": "portal-chip portal-chip-status-warn",
        "ROUTING_REVIEW": "portal-chip portal-chip-status-warn",
        "RESOLVED": "portal-chip portal-chip-status",
    }
    return mapping.get(status, "portal-chip portal-chip-status")


def _status_short_label(status: str) -> str:
    labels = {
        "ROUTED": "Open",
        "IN_PROGRESS": "In progress",
        "HUMAN_REVIEW": "Specialist review",
        "ESCALATED": "Needs specialist",
        "ROUTING_REVIEW": "Routing review",
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
        f'<p class="portal-brand">{html.escape(PRODUCT_NAME)}.</p>'
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
        f'<p class="portal-org">{html.escape(ORG_NAME)} Support Operations</p>'
        "</div>"
    )


def _queue_summary_html(
    department: str, total: int, mine: int, *, specialists: int = 0
) -> str:
    extra = ""
    if specialists:
        extra = (
            f'<p class="agent-queue-mine" style="margin-top:0.35rem;">'
            f"{specialists} in Routing Specialists desk</p>"
        )
    return _wrap(
        '<div class="agent-queue-card">'
        '<p class="agent-queue-lbl">Department queue</p>'
        f'<p class="agent-queue-dept">{html.escape(department)}</p>'
        f'<p class="agent-queue-val">{total}</p>'
        f'<p class="agent-queue-sub">active incident{"s" if total != 1 else ""}</p>'
        f'<p class="agent-queue-mine">{mine} assigned to you</p>'
        f"{extra}"
        "</div>"
    )


def _metrics_html(stats: dict, *, is_secops: bool = False) -> str:
    unassigned = stats["unassigned"]
    mine = stats["mine"]
    at_risk = stats["at_risk"]
    if is_secops:
        fourth_val = stats.get("specialists_count", 0)
        fourth_lbl = "Routing desk"
        fourth_hint = "Misroute review"
    else:
        fourth_val = stats["escalations"]
        fourth_lbl = "Specialist queue"
        fourth_hint = "Needs expert review"
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
        f'<p class="portal-metric-val">{fourth_val}</p>'
        f'<p class="portal-metric-lbl">{fourth_lbl}</p>'
        f'<p class="portal-metric-hint">{fourth_hint}</p></div></div>'
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


def _agent_toast(message: str, *, icon: str = "✅") -> None:
    st.session_state["agent_toast"] = message
    st.session_state["agent_toast_icon"] = icon


def _render_agent_toast() -> None:
    message = st.session_state.pop("agent_toast", None)
    if not message:
        return
    icon = st.session_state.pop("agent_toast_icon", "✅")
    st.toast(message, icon=icon)


def _sign_out() -> None:
    dark = st.session_state.get("dark_mode", False)
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["signed_in"] = False
    st.session_state["dark_mode"] = dark
    st.rerun()


def _open_ticket(ticket_id: str) -> None:
    _go_agent_detail(ticket_id)
    st.rerun()


def _open_reference_ticket(ref_ticket_id: str, return_to: str) -> None:
    """Open a RAG/historical reference ticket and allow return to the current ticket."""
    st.session_state["agent_return_ticket_id"] = return_to
    st.session_state["agent_reference_view"] = True
    st.session_state["agent_view"] = "detail"
    st.session_state["ticket_id"] = normalize_reference_ticket_id(ref_ticket_id)
    st.session_state["page"] = "agent"
    _sync_agent_url()
    st.rerun()


def _assign_ticket(session, ticket: Ticket, user: User) -> None:
    TicketStore(session).assign(ticket, user)
    _agent_toast(f"Ticket INC-{_ticket_key(ticket)} assigned to you.")
    st.rerun()


def _release_ticket(session, ticket: Ticket) -> None:
    TicketStore(session).release(ticket)
    _agent_toast(f"Ticket INC-{_ticket_key(ticket)} released to queue.", icon="ℹ️")
    st.rerun()


def _resolve_ticket(session, ticket: Ticket) -> None:
    TicketStore(session).resolve(ticket)
    _agent_toast(f"Ticket INC-{_ticket_key(ticket)} marked resolved.")
    session.refresh(ticket)
    st.rerun()


def _keep_specialist_in_secops(session, ticket: Ticket, user: User) -> None:
    ok, msg = keep_specialist_ticket_in_secops(session, ticket, user)
    if ok:
        _agent_toast(msg)
        _go_agent_home()
        st.rerun()
    else:
        st.error(msg)


def _send_to_specialists(session, ticket: Ticket, user: User, reason: str) -> None:
    ok, msg = request_specialist_review(session, ticket, user, reason)
    if ok:
        _agent_toast(msg, icon="🛡️")
        st.session_state.pop("agent_route_dialog_ticket", None)
        st.session_state.pop("specialist_reason_open", None)
        _go_agent_home()
        st.rerun()
    else:
        st.error(msg)


@st.dialog("Routing review")
def _agent_route_dialog(ticket_id: str, user: User, session) -> None:
    st.markdown(
        "<p style='margin:0 0 0.75rem;font-size:0.88rem;color:#475569;line-height:1.5;'>"
        "Explain why this ticket is misrouted. "
        f"Use at least {MIN_REASON_CHARS} characters."
        "</p>",
        unsafe_allow_html=True,
    )
    reason = st.text_area(
        "Reason",
        key=f"agent_route_reason_{ticket_id}",
        placeholder="e.g. This is a network VPN issue, not an application bug…",
        height=96,
        label_visibility="collapsed",
    )
    if st.button(
        "Submit route request",
        key=f"agent_route_submit_{ticket_id}",
        type="primary",
        use_container_width=True,
    ):
        ticket = TicketStore(session).get(ticket_id)
        if not ticket:
            st.error("Ticket not found.")
            return
        _send_to_specialists(session, ticket, user, reason)


def _render_route_action_cell(
    ticket: Ticket,
    user: User,
    session,
    ticket_id: str,
    *,
    key_suffix: str = "",
) -> None:
    """Route + SecOps badge — third Actions column (non-SecOps agents only)."""
    can_route = can_request_specialist(ticket, user) and _user_can_act_on_ticket(ticket, user)
    btn_key = f"agent_route_btn_{ticket_id}"
    if key_suffix:
        btn_key = f"{btn_key}_{key_suffix}"

    if st.button(
        "Route",
        key=btn_key,
        type="primary",
        disabled=not can_route,
        use_container_width=True,
    ):
        st.session_state["agent_route_dialog_ticket"] = ticket_id
        st.rerun()
    st.markdown(
        _wrap(
            '<p class="itsm-secops-badge">OPERATED BY <strong>SECOPS</strong></p>'
        ),
        unsafe_allow_html=True,
    )

    pending = st.session_state.get("agent_route_dialog_ticket")
    if pending == ticket_id:
        _agent_route_dialog(ticket_id, user, session)


def _render_agent_ticket_expanders(
    ticket: Ticket,
    session,
    ticket_id: str,
    *,
    clf: ClassificationArtifact | None,
    res: ResolutionArtifact | None,
    specialists_view: bool,
    reference_view: bool,
    corpus_ref: bool,
) -> None:
    desc = (ticket.description_sanitized or ticket.description_raw or "").strip()
    with st.expander("Incident description", expanded=False):
        if clf:
            sub = f" · {clf.subcategory}" if clf.subcategory else ""
            st.markdown(
                f'<p class="itsm-expander-meta">'
                f'<span class="itsm-expander-chip">Classification</span> '
                f"{html.escape(clf.use_case_category + sub)}</p>",
                unsafe_allow_html=True,
            )
        if desc:
            st.markdown(
                f'<p class="itsm-description-text">{html.escape(desc)}</p>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("No description recorded.")

    if specialists_view and not (reference_view or corpus_ref):
        ctx = get_specialist_context(session, ticket_id)
        with st.expander("Routing context", expanded=False):
            st.markdown(
                f'<p class="itsm-meta-val"><strong>Originally routed to:</strong> '
                f"{html.escape(str(ctx.get('original_department') or '—'))}</p>"
                f'<p class="itsm-meta-val"><strong>Flagged by:</strong> '
                f"{html.escape(str(ctx.get('requested_by') or '—'))}</p>"
                f'<p class="itsm-meta-val"><strong>Reason:</strong> '
                f"{html.escape(str(ctx.get('reason') or '—'))}</p>",
                unsafe_allow_html=True,
            )

    steps: list[str] = []
    references: list = []
    if res and ticket.hand in ("1", "2") and not specialists_view:
        _req_steps, assignee_steps = decode_steps(res.steps_json)
        steps = assignee_steps or _req_steps
        references = ArtifactStore.load_references(res)

    with st.expander("Resolution steps", expanded=False):
        if steps:
            step_items = "".join(
                f"<li style='margin-bottom:0.35rem;'>{html.escape(s)}</li>" for s in steps
            )
            st.markdown(
                f"<ol class='itsm-resolution-list'>{step_items}</ol>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("No resolution steps generated for this ticket.")
        if references and not (reference_view or corpus_ref):
            render_resolution_references(
                session,
                references,
                owner_ticket_id=ticket_id,
                key_prefix="agent",
                wrap=_wrap,
                open_reference=_open_reference_ticket,
            )


def _render_department_route_panel(
    session,
    ticket: Ticket,
    user: User,
    *,
    specialists: bool,
) -> None:
    """Premium department dropdown + Route (routing desk or SecOps operational)."""
    dept_options = list(OPERATIONAL_DEPARTMENT_QUEUES)
    mode = "specialists" if specialists else "secops"
    st.markdown(
        _wrap('<p class="itsm-section-title itsm-dept-route-heading">Route to department</p>'),
        unsafe_allow_html=True,
    )
    dept_col, btn_col = st.columns([2.35, 1], gap="small")
    with dept_col:
        target = st.selectbox(
            "Department",
            dept_options,
            format_func=display_department,
            key=f"dept_route_select_{mode}_{ticket.ticket_id}",
        )
    with btn_col:
        if st.button(
            "Route",
            key=f"dept_route_btn_{mode}_{ticket.ticket_id}",
            type="primary",
            use_container_width=True,
        ):
            if specialists:
                _confirm_specialist_reroute(session, ticket, user, target)
            else:
                _confirm_secops_reroute(session, ticket, user, target)


def _confirm_secops_reroute(
    session, ticket: Ticket, user: User, target_department: str
) -> None:
    ok, msg = reroute_secops_operational(session, ticket, user, target_department)
    if ok:
        _agent_toast(msg, icon="🛡️")
        _go_agent_home()
    else:
        st.error(msg)
    st.rerun()


def _confirm_specialist_reroute(
    session, ticket: Ticket, user: User, target_department: str
) -> None:
    ok, msg = reroute_from_specialists(session, ticket, user, target_department)
    if ok:
        _agent_toast(msg, icon="🛡️")
        _go_agent_home()
    else:
        st.error(msg)
    st.rerun()


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
    dept = user.department or "Infrastructure"
    dept_label = display_department(dept)
    name = _display_name(user.email)
    store = TicketStore(session)
    stats = store.department_stats(dept, user.user_id)

    _render_topnav("agent_signout")

    top_col1, top_col2 = st.columns([1, 1.4], gap="medium")
    with top_col1:
        st.markdown(_profile_card_html(name, user.email, dept_label), unsafe_allow_html=True)
    with top_col2:
        st.markdown(
            _queue_summary_html(
                dept_label,
                stats["total"],
                stats["mine"],
                specialists=stats.get("specialists_count", 0) if dept == "SecOps" else 0,
            ),
            unsafe_allow_html=True,
        )

    st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(_metrics_html(stats, is_secops=(dept == "SecOps")), unsafe_allow_html=True)

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

    with st.expander(f"Department inbox ({len(filtered)})", expanded=False):
        _render_queue_rows(filtered, user, session, "inbox")

    if dept == "SecOps":
        specialists = list_specialists_queue(session)
        spec_count = len(specialists)
        with st.expander(
            f"Routing Specialists desk ({spec_count})",
            expanded=False,
        ):
            st.markdown(
                _wrap(
                    '<p style="margin:0 0 0.5rem;font-size:0.8rem;font-weight:600;'
                    'color:#64748b;">Operated by SecOps team</p>'
                ),
                unsafe_allow_html=True,
            )
            if specialists:
                st.caption(
                    "Misrouted tickets from other teams awaiting correct department assignment."
                )
                _render_queue_rows(specialists, user, session, "specialists")
            else:
                st.caption("No tickets awaiting routing specialist review.")

        history = list_specialists_history(session)
        with st.expander(f"Routing desk history ({len(history)})", expanded=False):
            if history:
                st.caption(
                    "Tickets that passed through the routing specialists desk (audit trail)."
                )
                _render_resolved_rows(history[:12], user, session, "routing_hist")
            else:
                st.caption("No routing desk history yet.")

    resolved = stats.get("resolved_tickets") or []
    if resolved:
        with st.expander(f"Recently closed ({len(resolved)})", expanded=False):
            _render_resolved_rows(resolved[:8], user, session, "resolved")


def render_agent_detail(user: User, session, ticket_id: Optional[str]) -> None:
    if not ticket_id:
        st.warning("Select a ticket first.")
        return

    reference_view = bool(st.session_state.get("agent_reference_view"))
    ticket = (
        load_reference_ticket(session, ticket_id)
        if reference_view
        else TicketStore(session).get(ticket_id)
    )
    dept = user.department or "Infrastructure"
    dept_label = display_department(dept)
    corpus_ref = bool(ticket and is_reference_seed_id(ticket.ticket_id))

    if not ticket:
        st.error("Ticket not found.")
        return

    specialists_view = is_specialists_ticket(ticket)
    secops_user = (user.department or "") == "SecOps"

    if not (reference_view or corpus_ref):
        if specialists_view:
            if not secops_user:
                st.error("This ticket is in the SecOps Routing Specialists desk.")
                return
        elif not departments_match(ticket.department_queue, dept):
            st.error("Ticket not found or not in your department queue.")
            return
        elif ticket.hand not in ("2", "3"):
            st.error("This ticket is not in the assignee queue.")
            return

    clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket_id).first()
    res = session.query(ResolutionArtifact).filter_by(ticket_id=ticket_id).first()
    requester = session.get(User, ticket.user_id)
    req_name = _display_name(requester.email) if requester else "Unknown"
    hand_label, _, _ = HAND_DISPLAY.get(ticket.hand or "2", ("Team Assist", "", ""))
    confidence = ui.confidence_label(ticket.confidence)
    sla_txt, sla_cls = TicketStore(session).sla_label(ticket)
    key = _ticket_key(ticket)
    _render_topnav("agent_signout_detail")
    st.markdown(
        '<span class="ticket-detail-view" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )

    return_id = st.session_state.get("agent_return_ticket_id")
    if reference_view and return_id:
        if st.button("← Back to previous ticket", key="agent_detail_back_ref", type="tertiary"):
            st.session_state["ticket_id"] = return_id
            st.session_state.pop("agent_return_ticket_id", None)
            st.session_state.pop("agent_reference_view", None)
            _sync_agent_url()
            st.rerun()
    elif not (reference_view or corpus_ref):
        if st.button("← Back to dashboard", key="agent_detail_back_dashboard", type="tertiary"):
            _go_agent_home()
            st.rerun()

    if reference_view or corpus_ref:
        st.markdown(
            _wrap(
                '<div class="itsm-banner itsm-banner-ref">'
                "<strong>Reference ticket</strong> — "
                "Opened from resolution sources. Use for context when handling the active incident."
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    banner_cls = "itsm-banner-warn" if ticket.hand == "3" or specialists_view else "itsm-banner-info"
    if specialists_view:
        banner_head = "Routing Specialists — SecOps-owned desk"
        banner_body = (
            "An agent flagged a possible misroute. Confirm the correct department queue below."
        )
    elif ticket.hand == "3":
        banner_head = "Hand 3 — security specialist review"
        banner_body = (
            "Security escalation requires expert review before acting. "
            "Not the same as the Routing Specialists misroute desk."
        )
    else:
        banner_head = f"Routed assist — {dept_label} queue"
        banner_body = (
            "Resolution steps available below. Validate before closing with requester."
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
            f'<span class="itsm-chip itsm-chip-domain">{html.escape(dept_label)}</span>'
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

    _render_agent_ticket_expanders(
        ticket,
        session,
        ticket_id,
        clf=clf,
        res=res,
        specialists_view=specialists_view,
        reference_view=reference_view,
        corpus_ref=corpus_ref,
    )

    if not (reference_view or corpus_ref):
        st.markdown(
            _wrap('<p class="itsm-section-title itsm-detail-actions-title">Actions</p>'),
            unsafe_allow_html=True,
        )
        can_act = _user_can_act_on_ticket(ticket, user)
        owned_by_other = _ticket_owned_by_other(ticket, user)

        if owned_by_other:
            owner = _assignee_label(ticket, user, session)
            st.markdown(
                _wrap(
                    '<div class="itsm-section itsm-view-only-panel">'
                    "<p class='itsm-section-title'>View only</p>"
                    f"<p style='margin:0;color:#64748B;font-size:0.88rem;line-height:1.5;'>"
                    f"This ticket is owned by <strong>{html.escape(owner)}</strong>. "
                    "You can review details only until it is released back to the queue."
                    "</p></div>"
                ),
                unsafe_allow_html=True,
            )
        elif specialists_view and secops_user and ticket.status not in ("RESOLVED", "CLOSED"):
            st.caption(
                "Assign as SecOps security work, route to the correct department, or resolve."
            )
            ac1, ac2 = st.columns(2)
            with ac1:
                if not ticket.assignee_id or ticket.department_queue == SPECIALISTS_QUEUE:
                    if st.button(
                        "Assign to me (SecOps)",
                        key="specialist_keep_secops",
                        type="primary",
                        use_container_width=True,
                    ):
                        if ticket.department_queue == SPECIALISTS_QUEUE:
                            _keep_specialist_in_secops(session, ticket, user)
                        else:
                            _assign_ticket(session, ticket, user)
                elif ticket.assignee_id == user.user_id:
                    if st.button(
                        "Release to queue",
                        key="specialist_release",
                        use_container_width=True,
                    ):
                        _release_ticket(session, ticket)
            with ac2:
                if ticket.status != "RESOLVED":
                    if st.button(
                        "Mark resolved",
                        key="specialist_resolve",
                        type="primary",
                        use_container_width=True,
                    ):
                        _resolve_ticket(session, ticket)

            _render_department_route_panel(session, ticket, user, specialists=True)
        elif ticket.status not in ("RESOLVED", "CLOSED"):
            show_agent_route = not specialists_view and not owned_by_other and not secops_user
            show_secops_reroute = (
                secops_user and not specialists_view and not owned_by_other
            )
            if show_agent_route:
                ac1, ac2, ac3 = st.columns(3)
            else:
                ac1, ac2 = st.columns(2)
            with ac1:
                if not ticket.assignee_id:
                    if st.button(
                        "Assign to me",
                        key="agent_detail_assign",
                        type="primary",
                        use_container_width=True,
                    ):
                        _assign_ticket(session, ticket, user)
                elif ticket.assignee_id == user.user_id:
                    if st.button(
                        "Release to queue",
                        key="agent_detail_release",
                        use_container_width=True,
                    ):
                        _release_ticket(session, ticket)
            with ac2:
                if st.button(
                    "Mark resolved",
                    key="agent_detail_resolve",
                    type="primary",
                    use_container_width=True,
                ):
                    _resolve_ticket(session, ticket)
            if show_agent_route:
                with ac3:
                    _render_route_action_cell(ticket, user, session, ticket_id)
            if show_secops_reroute:
                _render_department_route_panel(session, ticket, user, specialists=False)
        elif ticket.status in ("RESOLVED", "CLOSED"):
            pass

    render_ticket_comments(session, ticket_id, user, _wrap, "agent")


def render_agent_portal(user: User, session) -> None:
    from src.services.auto_assign_service import run_auto_assignments

    _portal_scope_open()
    _restore_agent_state_from_url()
    run_auto_assignments(session)
    _render_agent_toast()
    if "agent_view" not in st.session_state:
        st.session_state["agent_view"] = "home"

    view = st.session_state["agent_view"]
    if view == "detail":
        render_agent_detail(user, session, st.session_state.get("ticket_id"))
    else:
        render_agent_home(user, session)

    _sync_agent_url()
