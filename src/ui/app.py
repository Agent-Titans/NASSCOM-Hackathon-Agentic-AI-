"""
SAARTHI — SaaS-style Streamlit dashboard.
Inspired by production Streamlit patterns (sidebar nav, KPIs, wide layout).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import streamlit as st
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config.brand import HAND_DISPLAY, PRODUCT_NAME, ROLE_DISPLAY, TAGLINE
from src.db.models import (
    AuditLog,
    ClassificationArtifact,
    Feedback,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.db.session import get_session_factory, init_db
from src.services.retrieval_bootstrap import start_retrieval_warm_background
from src.services.ticket_service import TicketService
from src.stores.ticket_store import TicketStore
from src.ui import components as ui

THEME = ROOT / "assets" / "theme.css"


def get_db() -> Session:
    """DB session only — retrieval index warms lazily on first ticket submit."""
    return get_session_factory()()


def _init_session() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "overview"


def sidebar_nav(user: User) -> str:
    """Role-based sidebar — returns selected page key."""
    ui.sidebar_brand()
    st.sidebar.markdown("##### Menu")

    pages: List[tuple[str, str, str]] = []
    if user.role == "requester":
        pages = [
            ("portal", "Portal", "Employee workspace"),
        ]
    elif user.role == "assignee":
        pages = [
            ("overview", "Overview", "Dashboard"),
            ("queue", "Team queue", "Assigned work"),
        ]
    else:
        pages = [
            ("overview", "Overview", "Dashboard"),
            ("audit", "Audit log", "Compliance"),
        ]

    current = st.session_state.get("page", "overview")
    for key, label, _ in pages:
        if st.sidebar.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if current == key else "secondary",
        ):
            st.session_state["page"] = key
            st.session_state.pop("ticket_id", None)
            if key == "portal":
                st.session_state["portal_view"] = "home"
            st.rerun()

    st.sidebar.markdown("---")
    ui.sidebar_user(user.email, user.role)
    if st.sidebar.button("Sign out", use_container_width=True):
        dark = st.session_state.get("dark_mode", False)
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state["signed_in"] = False
        st.session_state["dark_mode"] = dark
        st.rerun()

    return st.session_state.get("page", "overview")


def page_login() -> None:
    """Premium unified login card + dark mode toggle."""
    from src.ui.login_render import render_login_page

    render_login_page()


def stats_for_requester(user_id: str) -> dict:
    with get_db() as session:
        tickets = TicketStore(session).list_for_user(user_id)
    hands = Counter(t.hand for t in tickets if t.hand)
    return {
        "total": len(tickets),
        "self_help": hands.get("1", 0),
        "team": hands.get("2", 0),
        "specialist": hands.get("3", 0),
        "tickets": tickets,
    }


def stats_for_assignee(department: str) -> dict:
    with get_db() as session:
        tickets = TicketStore(session).list_for_department(department)
    return {"queue": len(tickets), "tickets": tickets}


def stats_admin() -> dict:
    with get_db() as session:
        total = session.query(func.count(Ticket.ticket_id)).scalar() or 0
        audits = session.query(func.count(AuditLog.audit_id)).scalar() or 0
    return {"tickets": total, "audits": audits}


def page_overview_requester(user: User) -> None:
    ui.hello_bar(user.email, user.role)
    st.caption("Overview · your support requests at a glance")
    s = stats_for_requester(user.user_id)
    ui.kpi_grid(
        [
            ("Total requests", str(s["total"]), "All time", True),
            ("Self-Help", str(s["self_help"]), "Resolved with steps", False),
            ("Team Assist", str(s["team"]), "Routed to IT", False),
            ("Specialist", str(s["specialist"]), "Human review", False),
        ]
    )
    with st.container(border=True):
        st.markdown("**Recent activity**")
        recent = s["tickets"][:5]
        if not recent:
            st.caption("No requests yet — create one from **New request**.")
        else:
            for t in recent:
                _, sub, _ = HAND_DISPLAY.get(t.hand or "", ("Pending", "", ""))
                st.markdown(
                    ui.ticket_row_html(
                        t.ticket_id,
                        t.title,
                        t.hand,
                        f"{sub} · {t.created_at.strftime('%b %d %H:%M')}",
                    ),
                    unsafe_allow_html=True,
                )
    if st.button("＋ New request", type="primary"):
        st.session_state["page"] = "new"
        st.rerun()


def page_requests(user: User) -> None:
    ui.hello_bar(user.email, user.role)
    st.caption("My requests · routed by five AI agents")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
    with get_db() as session:
        tickets = TicketStore(session).list_for_user(user.user_id)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("New request", type="primary", use_container_width=True):
            st.session_state["page"] = "new"
            st.rerun()
    if not tickets:
        ui.empty_state("No requests yet", "Submit your first issue — routing takes seconds.")
        return
    ui.panel_start(f"{len(tickets)} requests")
    for t in tickets:
        _, sub, _ = HAND_DISPLAY.get(t.hand or "", ("Pending", "", ""))
        st.markdown(
            ui.ticket_row_html(
                t.ticket_id,
                t.title,
                t.hand,
                f"{sub} · {t.status}",
                t.priority,
            ),
            unsafe_allow_html=True,
        )
        if st.button("View", key=f"v_{t.ticket_id}"):
            st.session_state["ticket_id"] = t.ticket_id
            st.session_state["page"] = "detail"
            st.rerun()
    ui.panel_end()


def page_new_request(user: User) -> None:
    ui.hello_bar(user.email, user.role)
    st.caption("New request · describe your issue (redacted before AI)")
    with st.form("create", border=False):
        c1, c2 = st.columns([2, 1])
        with c1:
            title = st.text_input("Subject", placeholder="Cannot reset password")
        with c2:
            urgency = st.selectbox("Urgency", ["low", "medium", "high"], index=1)
        description = st.text_area(
            "Details",
            height=120,
            placeholder="What happened? Include errors, device, and when it started.",
        )
        submitted = st.form_submit_button("Submit & route", type="primary", use_container_width=True)
    if submitted:
        if not title.strip() or not description.strip():
            st.error("Subject and details are required.")
            return
        try:
            with get_db() as session:
                ticket = TicketStore(session).create(
                    user, title.strip(), description.strip(), urgency
                )
                with st.spinner("Guardrail → Classify → Route → Resolve → Supervisor…"):
                    result = TicketService(session).process_ticket(ticket)
                hl, _, _ = HAND_DISPLAY[result.decision.hand]
                st.session_state["flash"] = (
                    f"Routed to {hl} · {result.classification.use_case_category}"
                )
                st.session_state["page"] = "requests"
                st.session_state["ticket_id"] = ticket.ticket_id
                st.rerun()
        except Exception as exc:
            st.error(str(exc))


def page_detail(user: User, ticket_id: Optional[str]) -> None:
    if not ticket_id:
        st.warning("Select a ticket first.")
        return
    with get_db() as session:
        ticket = TicketStore(session).get(ticket_id)
        if not ticket:
            st.error("Not found.")
            return
        if user.role == "requester" and ticket.user_id != user.user_id:
            st.error("Access denied.")
            return
        clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket_id).first()
        res = session.query(ResolutionArtifact).filter_by(ticket_id=ticket_id).first()
        audits = (
            session.query(AuditLog)
            .filter_by(ticket_id=ticket_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )
    label, sub, _ = HAND_DISPLAY.get(ticket.hand or "2", ("Team Assist", "", ""))
    ui.hello_bar(user.email, user.role)
    st.subheader(ticket.title)
    st.caption(sub)
    ui.kpi_grid(
        [
            ("Outcome", label, ticket.status, True),
            ("Confidence", ui.confidence_label(ticket.confidence), "Match strength", False),
            ("Queue", ticket.department_queue or "—", ticket.priority or "", False),
            ("SLA", f"{ticket.sla_hours}h" if ticket.sla_hours else "—", "Response target", False),
        ]
    )
    if clf:
        st.caption(f"Category: **{clf.use_case_category}** · source: {clf.source}")
    if ticket.hand == "3":
        st.info("Specialist review — no automated self-help steps (policy).")
    elif res:
        steps = json.loads(res.steps_json or "[]")
        if steps:
            with st.container(border=True):
                st.markdown("**Recommended steps**")
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. {step}")
        if ticket.hand == "1":
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Resolved", type="primary", use_container_width=True):
                    _feedback(ticket_id, "worked")
                    st.success("Thank you.")
            with c2:
                if st.button("Still need help", use_container_width=True):
                    _feedback(ticket_id, "failed")
                    _escalate(ticket_id)
                    st.rerun()
    ui.panel_start("Audit trail")
    for a in audits:
        ms = f" · {a.duration_ms}ms" if a.duration_ms else ""
        st.text(f"{a.timestamp:%H:%M:%S}  {a.agent or '—':12}  {a.event_type}{ms}")
    ui.panel_end()
    if st.button("← Back"):
        st.session_state["page"] = "requests" if user.role == "requester" else "queue"
        st.rerun()


def page_overview_assignee(user: User) -> None:
    ui.hello_bar(user.email, user.role)
    dept = user.department or "Hardware"
    st.caption(f"Team dashboard · {dept}")
    s = stats_for_assignee(dept)
    ui.kpi_grid(
        [
            ("In queue", str(s["queue"]), "Hand 2 & 3", True),
            ("Department", dept, "Your workspace", False),
            ("Agents", "5", "Pipeline active", False),
            ("SLA", "On", "Per priority", False),
        ]
    )
    page_queue(user, embedded=True)


def page_queue(user: User, embedded: bool = False) -> None:
    dept = user.department or "Hardware"
    if not embedded:
        ui.hello_bar(user.email, user.role)
        st.caption(f"Team queue · {dept}")
    s = stats_for_assignee(dept)
    if not s["tickets"]:
        ui.empty_state("Queue empty", "No Hand 2/3 tickets for your team right now.")
        return
    ui.panel_start(f"{len(s['tickets'])} tickets")
    for t in s["tickets"]:
        st.markdown(
            ui.ticket_row_html(
                t.ticket_id,
                t.title,
                t.hand,
                f"{t.status} · SLA {t.sla_hours}h",
                t.priority,
            ),
            unsafe_allow_html=True,
        )
        if st.button("Open", key=f"q_{t.ticket_id}"):
            st.session_state["ticket_id"] = t.ticket_id
            st.session_state["page"] = "detail"
            st.rerun()
    ui.panel_end()


def page_overview_admin(user: User) -> None:
    ui.hello_bar(user.email, user.role)
    st.caption("Admin · compliance and agent observability")
    s = stats_admin()
    ui.kpi_grid(
        [
            ("Tickets", str(s["tickets"]), "Total processed", True),
            ("Audit events", str(s["audits"]), "Append-only log", False),
            ("Agents", "5", "Fixed pipeline", False),
            ("Policy", "On", "Security → Specialist", False),
        ]
    )
    page_audit(user, embedded=True)


def page_audit(user: User, embedded: bool = False) -> None:
    if not embedded:
        ui.hello_bar(user.email, user.role)
        st.caption("Audit log · privacy-safe agent trace")
    with get_db() as session:
        rows = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    ui.panel_start("Recent events")
    if not rows:
        st.caption("No events yet.")
    else:
        for r in rows:
            st.text(
                f"{r.timestamp:%Y-%m-%d %H:%M}  {r.ticket_id[:8]}  "
                f"{r.agent or '-':12}  {r.event_type}"
            )
    ui.panel_end()


def _feedback(ticket_id: str, outcome: str) -> None:
    with get_db() as session:
        session.add(Feedback(ticket_id=ticket_id, outcome=outcome))
        session.commit()


def _escalate(ticket_id: str) -> None:
    """Requester opts out of self-help → Hand 3 specialist review."""
    with get_db() as session:
        t = TicketStore(session).get(ticket_id)
        if t:
            TicketStore(session).update_hand(
                t,
                hand="3",
                confidence=t.confidence or 0.5,
                status="HUMAN_REVIEW",
                department_queue=t.department_queue,
                priority=t.priority,
                sla_hours=t.sla_hours,
                escalation_required=True,
            )


def ensure_db() -> None:
    init_db()


def main() -> None:
    st.set_page_config(
        page_title=f"{PRODUCT_NAME} · {TAGLINE}",
        page_icon=None,
        layout="wide",
        initial_sidebar_state=(
            "collapsed"
            if "user" not in st.session_state
            or st.session_state.get("user", {}).get("role")
            in ("requester", "assignee", "admin")
            else "expanded"
        ),
    )
    ui.inject_theme(THEME)
    _init_session()
    if "saarthi_bootstrapped" not in st.session_state:
        ensure_db()
        st.session_state.saarthi_bootstrapped = True

    if "user" not in st.session_state:
        page_login()
        return

    with get_db() as session:
        user = session.get(User, st.session_state["user"]["user_id"])
        if not user:
            del st.session_state["user"]
            st.rerun()
            return

        if "retrieval_warm_started" not in st.session_state:
            st.session_state.retrieval_warm_started = True
            if user.role == "requester":
                start_retrieval_warm_background(delay_seconds=0.0, api_embeds=True)
            else:
                start_retrieval_warm_background(delay_seconds=2.0, api_embeds=False)

        if user.role == "requester":
            from src.ui.employee_portal import render_employee_portal

            st.session_state["page"] = "portal"
            render_employee_portal(user, session)
            return

        if user.role == "admin":
            from src.ui.admin_portal import render_admin_portal

            st.session_state["page"] = "admin"
            render_admin_portal(user, session)
            return

        if user.role == "assignee":
            from src.ui.agent_portal import render_agent_portal

            st.session_state["page"] = "agent"
            render_agent_portal(user, session)
            return

    page = sidebar_nav(user)
    tid = st.session_state.get("ticket_id")

    if page == "detail":
        page_detail(user, tid)
    else:
        if page == "audit":
            page_audit(user)
        else:
            page_overview_admin(user)


if __name__ == "__main__":
    main()
