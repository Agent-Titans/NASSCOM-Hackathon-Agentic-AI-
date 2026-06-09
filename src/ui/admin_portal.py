"""Helpdesk Admin Dashboard — KPI overview, triage, team load, audit."""
from __future__ import annotations

import csv
import html
import io
from datetime import datetime
from typing import Any, Optional

import streamlit as st

from src.db.models import AuditLog, Ticket, User
from src.services.admin_stats_service import AdminDashboardStats, get_admin_dashboard_stats
from src.ui.admin_portal_theme import admin_portal_css

_NAV_ITEMS = (
    ("dashboard", "OVERVIEW", "Dashboard", None),
    ("all_tickets", "TICKETS", "All Tickets", "total_tickets"),
    ("triage", "TICKETS", "Triage Queue", "triage_count"),
    ("team", "TEAM", "Team Workload", "near_capacity_teams"),
    ("settings", "SYSTEM", "Settings", None),
    ("audit", "SYSTEM", "Audit Log", None),
)

_REQUESTER_NAMES = {
    "requester@demo.local": "Karan Joshi",
    "emily.reed@demo.local": "Emily Reed",
    "james.wu@demo.local": "James Wu",
    "sarah.kim@demo.local": "Sarah Kim",
    "michael.brown@demo.local": "Michael Brown",
}

_AGENT_NAMES = {
    "hardware@demo.local": "Alex Chen",
    "software@demo.local": "Marcus Lee",
    "network@demo.local": "Priya Nair",
    "secops@demo.local": "Sam Ortiz",
    "identity@demo.local": "Jordan Kim",
    "dba@demo.local": "Riley Park",
    "storage@demo.local": "Casey Morgan",
}


def _wrap(inner: str) -> str:
    return f'<div class="premium-admin-scope">{inner}</div>'


def _scope_open() -> None:
    st.markdown(admin_portal_css(), unsafe_allow_html=True)
    st.markdown(
        '<div class="premium-admin-scope premium-admin-scope-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def _person_name(user_id: Optional[str], emails: dict[str, str]) -> str:
    if not user_id:
        return "—"
    email = emails.get(user_id, "")
    if email in _REQUESTER_NAMES:
        return _REQUESTER_NAMES[email]
    if email in _AGENT_NAMES:
        return _AGENT_NAMES[email]
    return email.split("@")[0].replace(".", " ").title() if email else "—"


def _ticket_inc(ticket: Ticket) -> str:
    return f"INC-{ticket.ticket_id[:8].upper()}"


def _bar_rows(items: list[tuple[str, int, str]], max_val: int) -> str:
    rows = []
    for label, val, css in items:
        pct = int(val / max_val * 100) if max_val else 0
        rows.append(
            f'<div class="admin-bar-row">'
            f'<span class="admin-bar-label">{html.escape(label)}</span>'
            f'<div class="admin-bar-track"><div class="admin-bar-fill {css}" '
            f'style="width:{pct}%"></div></div>'
            f'<span class="admin-bar-val">{val}</span></div>'
        )
    return "".join(rows)


def _status_label(status: str) -> str:
    if status in ("ROUTED", "IN_PROGRESS", "RECEIVED", "SELF_HELP"):
        return "Open"
    if status == "RESOLVED":
        return "Resolved"
    if status in ("HUMAN_REVIEW", "ESCALATED"):
        return "In Triage"
    if status == "CLOSED":
        return "Closed"
    return status.replace("_", " ").title()


def _status_pill(status: str) -> str:
    label = _status_label(status)
    if label == "Open":
        cls = "pill-open"
    elif label == "Resolved":
        cls = "pill-resolved"
    elif label == "In Triage":
        cls = "pill-triage"
    elif label == "Closed":
        cls = "pill-closed"
    else:
        cls = "pill-open"
    return f'<span class="admin-pill {cls}">{html.escape(label)}</span>'


def _hand_pill(hand: Optional[str]) -> str:
    if hand == "1":
        return '<span class="admin-pill pill-h1">Hand 1</span>'
    if hand == "2":
        return '<span class="admin-pill pill-h2">Hand 2</span>'
    if hand == "3":
        return '<span class="admin-pill pill-h3">Hand 3</span>'
    return '<span class="admin-pill pill-closed">—</span>'


def _time_ago(ticket: Ticket) -> str:
    if not ticket.created_at:
        return "—"
    delta = datetime.utcnow() - ticket.created_at
    hrs = int(delta.total_seconds() // 3600)
    return f"{hrs}h ago" if hrs < 48 else ticket.created_at.strftime("%b %d")


def _ticket_row_data(ticket: Ticket, stats: AdminDashboardStats) -> dict[str, Any]:
    return {
        "ticket": ticket,
        "id": _ticket_inc(ticket),
        "subject": ticket.title,
        "status": _status_label(ticket.status),
        "hand": f"Hand {ticket.hand}" if ticket.hand else "—",
        "department": ticket.department_queue or "—",
        "priority": ticket.priority or "—",
        "assignee": _person_name(ticket.assignee_id, stats.assignee_emails),
        "submitter": _person_name(ticket.user_id, stats.requester_emails),
        "time": _time_ago(ticket),
    }


def _unique_sorted(rows: list[dict[str, Any]], key: str) -> list[str]:
    vals = sorted({str(r[key]) for r in rows if r.get(key) and r[key] != "—"})
    return vals


# (field_key, header_label, filter_kind: "list" | "text")
_TICKET_COLUMN_FILTERS: list[tuple[str, str, str]] = [
    ("id", "ID", "list"),
    ("subject", "Subject", "text"),
    ("status", "Status", "list"),
    ("hand", "Hand", "list"),
    ("department", "Department", "list"),
    ("priority", "Priority", "list"),
    ("assignee", "Assigned To", "list"),
    ("submitter", "Submitter", "list"),
    ("time", "Time", "list"),
]
_TICKET_COL_WIDTHS = [1.05, 2.1, 0.95, 0.85, 1.05, 0.85, 1.15, 1.1, 0.85]

_AUDIT_COLUMN_FILTERS: list[tuple[str, str, str]] = [
    ("timestamp", "Time", "list"),
    ("ticket_ref", "Ticket", "list"),
    ("agent", "Agent", "list"),
    ("event", "Event", "list"),
    ("details", "Details", "text"),
]
_AUDIT_COL_WIDTHS = [1.15, 1.1, 1.1, 1.1, 2.4]


def _filter_state_key(table_key: str, field: str) -> str:
    return f"admin_col_filter_{table_key}_{field}"


def _header_filter_label(label: str, value: list[str] | str) -> str:
    if isinstance(value, list) and value:
        return f"{label} ({len(value)})"
    if isinstance(value, str) and value.strip():
        return f"{label} •"
    return f"{label} ▾"


def _apply_row_filters(
    rows: list[dict[str, Any]],
    *,
    list_filters: dict[str, list[str]],
    text_filters: dict[str, str],
) -> list[dict[str, Any]]:
    out = rows
    for field, selected in list_filters.items():
        if selected:
            allowed = set(selected)
            out = [r for r in out if str(r.get(field, "—")) in allowed]
    for field, query in text_filters.items():
        q = query.strip().lower()
        if q:
            out = [r for r in out if q in str(r.get(field, "")).lower()]
    return out


def _clear_column_filters(table_key: str, column_specs: list[tuple[str, str, str]]) -> None:
    for field, _, _ in column_specs:
        st.session_state.pop(_filter_state_key(table_key, field), None)


def _any_column_filter_active(
    column_specs: list[tuple[str, str, str]],
    table_key: str,
) -> bool:
    for field, _, kind in column_specs:
        val = st.session_state.get(_filter_state_key(table_key, field))
        if kind == "text" and isinstance(val, str) and val.strip():
            return True
        if kind == "list" and isinstance(val, list) and val:
            return True
    return False


def _render_column_header_filters(
    table_key: str,
    rows: list[dict[str, Any]],
    column_specs: list[tuple[str, str, str]],
    col_widths: list[float],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Clickable column headers — each opens a filter popover."""
    list_filters: dict[str, list[str]] = {}
    text_filters: dict[str, str] = {}
    cols = st.columns(col_widths)
    for col, (field, label, kind) in zip(cols, column_specs):
        state_key = _filter_state_key(table_key, field)
        with col:
            with st.container(key=f"admin_col_hdr_{table_key}_{field}"):
                if kind == "text":
                    current = st.session_state.get(state_key, "")
                    if not isinstance(current, str):
                        current = ""
                else:
                    current = st.session_state.get(state_key, [])
                    if not isinstance(current, list):
                        current = []

                hdr_label = _header_filter_label(label, current)

                with st.popover(hdr_label, use_container_width=True):
                    st.markdown(
                        _wrap(
                            f'<p class="admin-col-filter-title">Filter: {html.escape(label)}</p>'
                        ),
                        unsafe_allow_html=True,
                    )
                    if kind == "text":
                        text_filters[field] = st.text_input(
                            f"Contains — {label}",
                            key=state_key,
                            placeholder=f"Type to filter {label.lower()}…",
                            label_visibility="collapsed",
                        )
                    else:
                        options = _unique_sorted(rows, field)
                        list_filters[field] = st.multiselect(
                            f"Select — {label}",
                            options=options,
                            key=state_key,
                            placeholder=f"All {label}",
                            label_visibility="collapsed",
                        )

    for field, _, kind in column_specs:
        state_key = _filter_state_key(table_key, field)
        if kind == "text" and field not in text_filters:
            val = st.session_state.get(state_key, "")
            text_filters[field] = val if isinstance(val, str) else ""
        elif kind == "list" and field not in list_filters:
            val = st.session_state.get(state_key, [])
            list_filters[field] = val if isinstance(val, list) else []

    return list_filters, text_filters


def _render_filterable_table_shell(
    title: str,
    table_key: str,
    rows: list[dict[str, Any]],
    column_specs: list[tuple[str, str, str]],
    col_widths: list[float],
) -> list[dict[str, Any]]:
    st.markdown(
        _wrap(
            f'<div class="admin-card admin-table-card"><h3 style="margin-bottom:0.5rem">'
            f"{html.escape(title)}</h3>"
        ),
        unsafe_allow_html=True,
    )

    list_filters, text_filters = _render_column_header_filters(
        table_key, rows, column_specs, col_widths
    )
    filtered = _apply_row_filters(rows, list_filters=list_filters, text_filters=text_filters)

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(
            _wrap(
                f'<p class="admin-filter-count">Showing {len(filtered)} of {len(rows)} rows</p>'
            ),
            unsafe_allow_html=True,
        )
    with c2:
        if st.button(
            "Clear filters",
            key=f"admin_col_filter_clear_{table_key}",
            use_container_width=True,
            disabled=not _any_column_filter_active(column_specs, table_key),
        ):
            _clear_column_filters(table_key, column_specs)
            st.rerun()

    return filtered


def _tickets_csv(tickets: list[Ticket], emails: dict[str, str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["ID", "Subject", "Status", "Hand", "Department", "Assignee", "Submitter", "Created"]
    )
    for t in tickets:
        writer.writerow(
            [
                _ticket_inc(t),
                t.title,
                t.status,
                t.hand or "",
                t.department_queue or "",
                _person_name(t.assignee_id, emails),
                _person_name(t.user_id, emails),
                t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "",
            ]
        )
    return buf.getvalue()


def _admin_sign_out() -> None:
    dark = st.session_state.get("dark_mode", False)
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["signed_in"] = False
    st.session_state["dark_mode"] = dark
    st.rerun()


def _render_topnav(user: User) -> None:
    display = "Super Admin" if user.role == "admin" else user.email.split("@")[0].title()
    st.markdown(
        _wrap(
            '<header class="admin-topnav">'
            '<p class="portal-brand">ClearHand.</p>'
            f'<span class="admin-topnav-meta">{html.escape(display)} · Admin Console</span>'
            "</header>"
        ),
        unsafe_allow_html=True,
    )
    if st.button("Sign out", key="admin_signout"):
        _admin_sign_out()


def _render_nav_bar(stats: AdminDashboardStats, view: str) -> None:
    """Horizontal nav — matches Employee / Agent top-level pattern (no left sidebar)."""
    cols = st.columns(len(_NAV_ITEMS))
    for col, (key, _section, label, badge_key) in zip(cols, _NAV_ITEMS):
        badge_val = getattr(stats, badge_key, None) if badge_key else None
        btn_label = f"{label} ({badge_val})" if badge_val is not None else label
        with col:
            if st.button(
                btn_label,
                key=f"admin_nav_{key}",
                use_container_width=True,
                type="primary" if view == key else "secondary",
            ):
                st.session_state["admin_view"] = key
                st.session_state.pop("admin_ticket_id", None)
                st.rerun()


def _header(title: str, subtitle: str, export_csv: str) -> None:
    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        st.markdown(
            _wrap(
                f'<div class="admin-header">'
                f"<div><h1>{html.escape(title)}</h1>"
                f"<p>{html.escape(subtitle)}</p></div></div>"
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.download_button(
            "Export",
            data=export_csv,
            file_name=f"helpdesk-export-{datetime.utcnow():%Y%m%d}.csv",
            mime="text/csv",
            key="admin_hdr_export",
            use_container_width=True,
        )
    with c3:
        if st.button("Refresh", key="admin_hdr_refresh", use_container_width=True):
            st.rerun()


def _render_dashboard(stats: AdminDashboardStats) -> None:
    today = datetime.utcnow().strftime("%b %d, %Y")
    _header("Dashboard", f"Real-time overview — {today}", _tickets_csv(stats.all_tickets, stats.requester_emails))

    trend_total = ""
    if stats.total_week_delta_pct is not None:
        arrow = "↑" if stats.total_week_delta_pct >= 0 else "↓"
        cls = "admin-trend-up" if stats.total_week_delta_pct >= 0 else "admin-trend-down"
        trend_total = (
            f'<span class="{cls}">{arrow} {abs(stats.total_week_delta_pct)}% vs last week</span>'
        )

    trend_res = ""
    if stats.resolution_week_delta_h is not None:
        arrow = "↑" if stats.resolution_week_delta_h > 0 else "↓"
        cls = "admin-trend-down" if stats.resolution_week_delta_h > 0 else "admin-trend-up"
        trend_res = (
            f'<span class="{cls}">{arrow} {abs(stats.resolution_week_delta_h)}h vs last week</span>'
        )

    st.markdown(
        _wrap(
            f'<div class="admin-kpi-grid">'
            f'<div class="admin-kpi"><p class="label">Total Tickets</p>'
            f'<p class="value">{stats.total_tickets}</p>'
            f'<p class="sub">{trend_total}</p></div>'
            f'<div class="admin-kpi"><p class="label">Open</p>'
            f'<p class="value">{stats.open_count}</p>'
            f'<p class="sub">{stats.with_agent} with agent · {stats.pending_user} pending user</p></div>'
            f'<div class="admin-kpi"><p class="label">Avg Resolution Time</p>'
            f'<p class="value">{stats.avg_resolution_hours}h</p>'
            f'<p class="sub">{trend_res}</p></div>'
            f'<div class="admin-kpi"><p class="label">Auto-Resolved (Hand 1)</p>'
            f'<p class="value">{stats.auto_resolved_pct}%</p>'
            f'<p class="sub admin-trend-good">{stats.auto_resolved_count} of {stats.total_tickets} total</p></div>'
            f"</div>"
        ),
        unsafe_allow_html=True,
    )

    h1 = stats.hand_counts.get("1", 0)
    h2 = stats.hand_counts.get("2", 0)
    h3 = stats.hand_counts.get("3", 0)
    hand_max = max(h1, h2, h3, 1)
    open_c = stats.status_counts.get("Open", 0)
    res_c = stats.status_counts.get("Resolved", 0)
    closed_c = stats.status_counts.get("Closed", 0)
    triage_c = stats.status_counts.get("In Triage", 0)
    status_max = max(open_c, res_c, closed_c, triage_c, 1)

    routed = h1 + h2 + h3 or 1
    high_pct = int(stats.confidence_high / routed * 100)
    med_pct = int(stats.confidence_medium / routed * 100)
    low_pct = int(stats.confidence_low / routed * 100)

    st.markdown(
        _wrap(
            '<div class="admin-mid-grid">'
            '<div class="admin-card"><h3>Tickets by AI Hand</h3>'
            + _bar_rows(
                [("Hand 1", h1, "fill-h1"), ("Hand 2", h2, "fill-h2"), ("Hand 3", h3, "fill-h3")],
                hand_max,
            )
            + f'<div class="admin-conf-footer">'
            f'<span class="admin-conf-pill conf-high">{high_pct}% High Confidence</span>'
            f'<span class="admin-conf-pill conf-med">{med_pct}% Medium</span>'
            f'<span class="admin-conf-pill conf-low">{low_pct}% No Match</span>'
            f"</div></div>"
            '<div class="admin-card"><h3>Status Breakdown</h3>'
            + _bar_rows(
                [
                    ("Open", open_c, "fill-open"),
                    ("Resolved", res_c, "fill-resolved"),
                    ("Closed", closed_c, "fill-closed"),
                    ("In Triage", triage_c, "fill-triage"),
                ],
                status_max,
            )
            + "</div></div>"
        ),
        unsafe_allow_html=True,
    )

    team_cards = []
    for team in stats.team_loads[:3]:
        cap_cls = "cap-ok"
        if team.capacity_pct >= 80:
            cap_cls = "cap-danger"
        elif team.capacity_pct >= 70:
            cap_cls = "cap-warn"
        team_cards.append(
            f'<div class="admin-card admin-team-card">'
            f"<h4>{html.escape(team.name)}</h4>"
            f'<p class="open-count">{team.open_count} open</p>'
            f'<p class="meta">{html.escape(team.note)}</p>'
            f'<div class="admin-cap-track"><div class="admin-cap-fill {cap_cls}" '
            f'style="width:{team.capacity_pct}%"></div></div>'
            f'<p class="admin-cap-label">{team.capacity_pct}% capacity</p></div>'
        )
    while len(team_cards) < 3:
        team_cards.append(
            '<div class="admin-card admin-team-card">'
            "<h4>—</h4><p class='open-count'>0 open</p>"
            "<p class='meta'>No load data</p></div>"
        )

    st.markdown(
        _wrap(f'<div class="admin-team-grid">{"".join(team_cards)}</div>'),
        unsafe_allow_html=True,
    )

    _render_ticket_table(
        stats.recent_tickets,
        stats,
        title="Recent Activity",
        table_key="recent",
    )


def _render_ticket_table(
    tickets: list[Ticket],
    stats: AdminDashboardStats,
    *,
    title: str = "Tickets",
    table_key: str = "tickets",
) -> None:
    row_data = [_ticket_row_data(t, stats) for t in tickets]
    filtered = _render_filterable_table_shell(
        title,
        table_key,
        row_data,
        _TICKET_COLUMN_FILTERS,
        _TICKET_COL_WIDTHS,
    )

    html_rows = []
    for r in filtered:
        t = r["ticket"]
        html_rows.append(
            "<tr>"
            f'<td><span class="admin-id">{html.escape(r["id"])}</span></td>'
            f"<td>{html.escape(r['subject'][:48])}</td>"
            f"<td>{_status_pill(t.status)}</td>"
            f"<td>{_hand_pill(t.hand)}</td>"
            f"<td>{html.escape(r['department'])}</td>"
            f"<td>{html.escape(r['priority'])}</td>"
            f"<td>{html.escape(r['assignee'])}</td>"
            f"<td>{html.escape(r['submitter'])}</td>"
            f"<td>{html.escape(r['time'])}</td>"
            "</tr>"
        )
    body = "".join(html_rows) if html_rows else (
        "<tr><td colspan='9' style='color:#94A3B8;padding:1rem'>"
        "No tickets match your filters.</td></tr>"
    )
    st.markdown(
        _wrap(
            '<div class="admin-table-wrap admin-table-wrap-body">'
            f"<table class='admin-table admin-table-body-only'><tbody>{body}</tbody></table>"
            "</div></div>"
        ),
        unsafe_allow_html=True,
    )


def _render_all_tickets(stats: AdminDashboardStats) -> None:
    _header(
        "All Tickets",
        f"{stats.total_tickets} tickets in the system",
        _tickets_csv(stats.all_tickets, stats.requester_emails),
    )
    _render_ticket_table(
        stats.all_tickets,
        stats,
        title="All Tickets",
        table_key="all",
    )


def _render_triage(stats: AdminDashboardStats) -> None:
    open_triage = [t for t in stats.triage_tickets if t.status not in ("RESOLVED", "CLOSED")]
    _header(
        "Triage Queue",
        f"{len(open_triage)} tickets awaiting specialist review",
        _tickets_csv(open_triage, stats.requester_emails),
    )
    _render_ticket_table(
        open_triage,
        stats,
        title="Triage Queue",
        table_key="triage",
    )


def _render_team(stats: AdminDashboardStats) -> None:
    _header(
        "Team Workload",
        f"{stats.near_capacity_teams} teams near capacity",
        _tickets_csv(stats.all_tickets, stats.requester_emails),
    )
    cards = []
    for team in stats.team_loads:
        cap_cls = "cap-ok"
        if team.capacity_pct >= 80:
            cap_cls = "cap-danger"
        elif team.capacity_pct >= 70:
            cap_cls = "cap-warn"
        cards.append(
            f'<div class="admin-card admin-team-card">'
            f"<h4>{html.escape(team.name)}</h4>"
            f'<p class="open-count">{team.open_count} open</p>'
            f'<p class="meta">{team.agent_count} agents · {html.escape(team.note)}</p>'
            f'<div class="admin-cap-track"><div class="admin-cap-fill {cap_cls}" '
            f'style="width:{team.capacity_pct}%"></div></div>'
            f'<p class="admin-cap-label">{team.capacity_pct}% capacity</p></div>'
        )
    st.markdown(
        _wrap(f'<div class="admin-team-grid">{"".join(cards) or "<p>No teams</p>"}</div>'),
        unsafe_allow_html=True,
    )


def _render_settings() -> None:
    _header("Settings", "System policy and pipeline configuration", "ID,Subject\n")
    st.markdown(
        _wrap(
            '<div class="admin-card">'
            "<h3>Routing policy</h3>"
            "<p style='color:#64748B;font-size:0.85rem;margin:0 0 0.75rem'>"
            "Security category always routes to Hand 3 (SecOps). "
            "Supervisor uses c_total bands: Hand 1 ≥ 0.80, Hand 2 ≥ 0.60.</p>"
            "<h3 style='margin-top:1rem'>RAG corpus</h3>"
            "<p style='color:#64748B;font-size:0.85rem;margin:0'>"
            "Run <code>python scripts/seed_rag_demo_tickets.py</code> to refresh "
            "ChromaDB demo tickets (45 samples, 15 per Hand).</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_audit(session) -> None:
    audit_rows = (
        session.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
        .all()
    )
    _header("Audit Log", "Privacy-safe agent trace (append-only)", "Time,Ticket,Agent,Event\n")

    row_data = [
        {
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M") if r.timestamp else "—",
            "ticket_ref": f"INC-{r.ticket_id[:8].upper()}",
            "agent": r.agent or "—",
            "event": r.event_type,
            "details": (r.details or "")[:120],
            "_raw": r,
        }
        for r in audit_rows
    ]
    filtered = _render_filterable_table_shell(
        "Recent events",
        "audit",
        row_data,
        _AUDIT_COLUMN_FILTERS,
        _AUDIT_COL_WIDTHS,
    )

    lines = []
    for r in filtered:
        lines.append(
            "<tr>"
            f"<td>{html.escape(r['timestamp'])}</td>"
            f'<td><span class="admin-id">{html.escape(r["ticket_ref"])}</span></td>'
            f"<td>{html.escape(r['agent'])}</td>"
            f"<td>{html.escape(r['event'])}</td>"
            f"<td>{html.escape(r['details'])}</td>"
            "</tr>"
        )
    body = "".join(lines) if lines else (
        "<tr><td colspan='5' style='color:#94A3B8;padding:1rem'>"
        "No events match your filters.</td></tr>"
    )
    st.markdown(
        _wrap(
            '<div class="admin-table-wrap admin-table-wrap-body">'
            f"<table class='admin-table admin-table-body-only'><tbody>{body}</tbody></table>"
            "</div></div>"
        ),
        unsafe_allow_html=True,
    )


def render_admin_portal(user: User, session) -> None:
    _scope_open()
    if "admin_view" not in st.session_state:
        st.session_state["admin_view"] = "dashboard"

    stats = get_admin_dashboard_stats(session)
    view = st.session_state["admin_view"]

    _render_topnav(user)
    _render_nav_bar(stats, view)

    if view == "dashboard":
        _render_dashboard(stats)
    elif view == "all_tickets":
        _render_all_tickets(stats)
    elif view == "triage":
        _render_triage(stats)
    elif view == "team":
        _render_team(stats)
    elif view == "settings":
        _render_settings()
    elif view == "audit":
        _render_audit(session)
    else:
        _render_dashboard(stats)
