"""Helpdesk Admin Dashboard — KPI overview, tickets, audit."""
from __future__ import annotations

import csv
import html
import io
import re
import time
from datetime import datetime
from typing import Any, Optional

import streamlit as st

from src.config.brand import PRODUCT_NAME
from src.config.departments import display_department
from src.config.demo_profiles import demo_person_name
from src.db.models import AuditLog, ClassificationArtifact, ResolutionArtifact, Ticket, User
from src.services.admin_stats_service import AdminDashboardStats, get_admin_dashboard_stats
from src.services.resolution_steps_codec import decode_steps
from src.stores.ticket_store import TicketStore
from src.ui import components as ui
from src.ui.admin_portal_theme import admin_portal_css
from src.ui.team_presence import refresh_presence_states, schedule_presence_rerun, team_members_html
from src.ui.ticket_display import assignee_name, department_label, hand_routing_label

_NAV_ITEMS = (
    ("dashboard", "OVERVIEW", "Dashboard", None),
    ("all_tickets", "TICKETS", "All Tickets", "total_tickets"),
    ("audit", "SYSTEM", "Audit Log", None),
)

_ADMIN_STATS_TTL_SEC = 45.0


def _cached_admin_stats(session) -> AdminDashboardStats:
    now = time.monotonic()
    cached_at = float(st.session_state.get("_admin_stats_at", 0.0))
    cached = st.session_state.get("_admin_stats")
    if cached is not None and (now - cached_at) < _ADMIN_STATS_TTL_SEC:
        return cached
    stats = get_admin_dashboard_stats(session)
    st.session_state["_admin_stats"] = stats
    st.session_state["_admin_stats_at"] = now
    return stats


def invalidate_admin_stats_cache() -> None:
    st.session_state.pop("_admin_stats", None)
    st.session_state.pop("_admin_stats_at", None)

_RAG_DETAIL_RE = re.compile(r"ticket=([a-f0-9]{8})\s+score=([\d.]+)")

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
    return demo_person_name(email) if email else "—"


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
        "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M") if ticket.created_at else "—",
        "id": _ticket_inc(ticket),
        "subject": ticket.title,
        "status": _status_label(ticket.status),
        "hand": f"Hand {ticket.hand}" if ticket.hand else "—",
        "department": display_department(ticket.department_queue)
        if ticket.department_queue
        else "—",
        "priority": ticket.priority or "—",
        "assignee": _person_name(ticket.assignee_id, stats.assignee_emails),
        "submitter": _person_name(ticket.user_id, stats.requester_emails),
        "time": _time_ago(ticket),
    }


def _unique_sorted(rows: list[dict[str, Any]], key: str) -> list[str]:
    vals = sorted({str(r[key]) for r in rows if r.get(key) and r[key] != "—"})
    return vals


# (field_key, header_label, filter_kind: "list" | "text")
_ALL_TICKETS_COLUMN_FILTERS: list[tuple[str, str, str]] = [
    ("created_at", "Created", "list"),
    ("id", "Ticket", "list"),
    ("subject", "Title", "text"),
    ("status", "Status", "list"),
    ("hand", "Hand", "list"),
    ("department", "Team", "list"),
    ("assignee", "Assignee", "list"),
    ("priority", "Prio", "list"),
]
_ALL_TICKETS_COL_WIDTHS = [1.05, 0.95, 1.7, 0.82, 0.72, 0.95, 1.0, 0.82]

_AUDIT_COLUMN_FILTERS: list[tuple[str, str, str]] = [
    ("created_at", "Created", "list"),
    ("ticket_ref", "Ticket", "list"),
    ("subject", "Title", "text"),
    ("hand", "Hand", "list"),
    ("confidence_match", "Conf / Match", "text"),
    ("team", "Team", "list"),
    ("assignee", "Assignee", "list"),
    ("sla", "SLA", "list"),
    ("priority", "Prio", "list"),
]
_AUDIT_COL_WIDTHS = [1.05, 0.95, 1.7, 0.72, 1.4, 0.95, 1.0, 0.78, 0.82]

# Short filter-button labels; popover still uses the full name.
_FILTER_POPOVER_TITLES: dict[str, str] = {
    "priority": "Priority",
}


def _filter_state_key(table_key: str, field: str) -> str:
    return f"admin_col_filter_{table_key}_{field}"


def _col_percentages(widths: list[float]) -> list[str]:
    total = sum(widths) or 1.0
    return [f"{w / total * 100:.4f}%" for w in widths]


def _colgroup_html(widths: list[float]) -> str:
    return "".join(f'<col style="width:{pct}">' for pct in _col_percentages(widths))


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

                popover_title = _FILTER_POPOVER_TITLES.get(field, label)
                with st.popover(hdr_label, use_container_width=True):
                    st.markdown(
                        _wrap(
                            f'<p class="admin-col-filter-title">Filter: {html.escape(popover_title)}</p>'
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


def _read_column_filter_state(
    table_key: str,
    column_specs: list[tuple[str, str, str]],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    list_filters: dict[str, list[str]] = {}
    text_filters: dict[str, str] = {}
    for field, _, kind in column_specs:
        state_key = _filter_state_key(table_key, field)
        if kind == "text":
            val = st.session_state.get(state_key, "")
            text_filters[field] = val if isinstance(val, str) else ""
        else:
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
    preview_list, preview_text = _read_column_filter_state(table_key, column_specs)
    preview = _apply_row_filters(
        rows, list_filters=preview_list, text_filters=preview_text
    )

    st.markdown(
        _wrap(f'<div class="admin-table-panel" data-admin-table="{html.escape(table_key)}">'),
        unsafe_allow_html=True,
    )
    toolbar_l, toolbar_r = st.columns([5.5, 1])
    with toolbar_l:
        st.markdown(
            _wrap(
                f'<div class="admin-table-toolbar">'
                f"<h3>{html.escape(title)}</h3>"
                f'<span class="admin-filter-count">Showing {len(preview)} of {len(rows)} rows</span>'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )
    with toolbar_r:
        st.markdown(_wrap('<div class="admin-table-clear-wrap">'), unsafe_allow_html=True)
        if st.button(
            "Clear filters",
            key=f"admin_col_filter_clear_{table_key}",
            use_container_width=True,
            disabled=not _any_column_filter_active(column_specs, table_key),
        ):
            _clear_column_filters(table_key, column_specs)
            st.rerun()

    list_filters, text_filters = _render_column_header_filters(
        table_key, rows, column_specs, col_widths
    )
    return _apply_row_filters(rows, list_filters=list_filters, text_filters=text_filters)


def _close_admin_table_panel() -> None:
    st.markdown(_wrap("</div>"), unsafe_allow_html=True)


def _open_admin_ticket(ticket_id: str) -> None:
    st.session_state["admin_ticket_id"] = ticket_id
    st.session_state["admin_view"] = "all_tickets"
    st.rerun()


def _all_tickets_csv(tickets: list[Ticket], emails: dict[str, str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Subject", "Status", "Department", "Assignee"])
    for t in tickets:
        writer.writerow(
            [
                _ticket_inc(t),
                t.title,
                _status_label(t.status),
                display_department(t.department_queue) if t.department_queue else "",
                _person_name(t.assignee_id, emails),
            ]
        )
    return buf.getvalue()


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
            f'<p class="portal-brand">{html.escape(PRODUCT_NAME)}.</p>'
            f'<span class="admin-topnav-meta">{html.escape(display)} · Admin Console</span>'
            "</header>"
        ),
        unsafe_allow_html=True,
    )
    if st.button("Sign out", key="admin_signout"):
        _admin_sign_out()


def _render_nav_bar(stats: AdminDashboardStats, view: str) -> None:
    """Horizontal nav — matches Employee / Agent top-level pattern (no left sidebar)."""
    st.markdown(_wrap('<div class="admin-nav-row">'), unsafe_allow_html=True)
    cols = st.columns(len(_NAV_ITEMS), gap="small")
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
    st.markdown(_wrap("</div>"), unsafe_allow_html=True)


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
            f'<p class="sub">{stats.with_agent} with agent · {stats.pending_user} pending user'
            f' · {stats.specialists_open} routing desk</p></div>'
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
    routing_c = stats.status_counts.get("Routing Specialists", 0)
    status_max = max(open_c, res_c, closed_c, triage_c, routing_c, 1)

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
                    ("Routing Specialists", routing_c, "fill-triage"),
                ],
                status_max,
            )
            + "</div></div>"
        ),
        unsafe_allow_html=True,
    )

    presence = refresh_presence_states()
    team_cards = []
    for team in stats.team_loads:
        cap_cls = "cap-ok"
        if team.capacity_pct >= 80:
            cap_cls = "cap-danger"
        elif team.capacity_pct >= 70:
            cap_cls = "cap-warn"
        members_block = team_members_html(team.name, presence)
        team_cards.append(
            f'<div class="admin-card admin-team-card">'
            f"<h4>{html.escape(team.name)}</h4>"
            f'<p class="open-count">{team.open_count} open</p>'
            f'<p class="meta">{html.escape(team.note)}</p>'
            f'<div class="admin-cap-track"><div class="admin-cap-fill {cap_cls}" '
            f'style="width:{team.capacity_pct}%"></div></div>'
            f'<p class="admin-cap-label">{team.capacity_pct}% capacity</p>'
            f"{members_block}</div>"
        )

    st.markdown(
        _wrap(f'<div class="admin-team-grid">{"".join(team_cards)}</div>'),
        unsafe_allow_html=True,
    )
    schedule_presence_rerun()


def _render_admin_html_table(
    rows: list[dict[str, Any]],
    col_widths: list[float],
    *,
    build_cells: Any,
    empty_colspan: int,
) -> None:
    lines = []
    for r in rows:
        t = r["ticket"]
        lines.append("<tr>" + build_cells(r, t) + "</tr>")
    colgroup = _colgroup_html(col_widths)
    body = "".join(lines) if lines else (
        f"<tr><td colspan='{empty_colspan}' style='color:#94A3B8;padding:1rem'>"
        "No tickets match your filters.</td></tr>"
    )
    st.markdown(
        _wrap(
            '<div class="admin-table-data admin-table-data-html">'
            f"<table class='admin-table admin-table-body-only admin-table-fixed'>"
            f"<colgroup>{colgroup}</colgroup><tbody>{body}</tbody></table>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_all_tickets(stats: AdminDashboardStats) -> None:
    _header(
        "All Tickets",
        f"{stats.total_tickets} tickets in the system",
        _all_tickets_csv(stats.all_tickets, stats.assignee_emails),
    )
    row_data = [_ticket_row_data(t, stats) for t in stats.all_tickets]
    filtered = _render_filterable_table_shell(
        "All tickets",
        "all",
        row_data,
        _ALL_TICKETS_COLUMN_FILTERS,
        _ALL_TICKETS_COL_WIDTHS,
    )

    if filtered:
        open_options = {
            f"{r['id']} — {r['subject'][:48]}": r["ticket"].ticket_id for r in filtered
        }
        pick_col, view_col = st.columns([5, 1], gap="small")
        with pick_col:
            choice = st.selectbox(
                "Open ticket detail",
                list(open_options.keys()),
                key="admin_pick_ticket",
                index=None,
                placeholder="Select a ticket to view details…",
                label_visibility="collapsed",
            )
        with view_col:
            if st.button(
                "View",
                key="admin_pick_view",
                use_container_width=True,
                disabled=choice is None,
            ):
                _open_admin_ticket(open_options[choice])

    def _all_ticket_cells(r: dict[str, Any], t: Ticket) -> str:
        return (
            f"<td>{html.escape(r['created_at'])}</td>"
            f'<td><span class="admin-id">{html.escape(r["id"])}</span></td>'
            f'<td class="admin-cell-wrap">{html.escape(r["subject"][:64])}</td>'
            f"<td>{_status_pill(t.status)}</td>"
            f"<td>{_hand_pill(t.hand)}</td>"
            f"<td>{html.escape(r['department'])}</td>"
            f"<td>{html.escape(r['assignee'])}</td>"
            f"<td>{html.escape(r['priority'])}</td>"
        )

    _render_admin_html_table(
        filtered,
        _ALL_TICKETS_COL_WIDTHS,
        build_cells=_all_ticket_cells,
        empty_colspan=len(_ALL_TICKETS_COLUMN_FILTERS),
    )
    _close_admin_table_panel()


def _render_admin_ticket_detail(user: User, session, ticket_id: str) -> None:
    ticket = TicketStore(session).get(ticket_id)
    if not ticket:
        st.error("Ticket not found.")
        if st.button("← Back to All Tickets", key="admin_detail_missing_back", type="tertiary"):
            st.session_state.pop("admin_ticket_id", None)
            st.rerun()
        return

    clf = session.query(ClassificationArtifact).filter_by(ticket_id=ticket_id).first()
    res = session.query(ResolutionArtifact).filter_by(ticket_id=ticket_id).first()
    requester = session.get(User, ticket.user_id)
    req_name = demo_person_name(requester.email) if requester else "Unknown"
    sla_txt, sla_cls = TicketStore(session).sla_label(ticket)
    confidence = ui.confidence_label(ticket.confidence)

    if st.button("← Back to All Tickets", key="admin_detail_back", type="tertiary"):
        st.session_state.pop("admin_ticket_id", None)
        st.session_state["admin_view"] = "all_tickets"
        st.rerun()

    st.markdown(
        _wrap(
            f'<div class="admin-card admin-ticket-detail">'
            f'<p class="admin-ticket-detail-id">{html.escape(_ticket_inc(ticket))}</p>'
            f"<h2>{html.escape(ticket.title)}</h2>"
            f'<div class="admin-ticket-detail-chips">'
            f"{_status_pill(ticket.status)}"
            f"{_hand_pill(ticket.hand)}"
            f"</div>"
            f'<div class="admin-ticket-meta-grid">'
            f"<div><p class=\"meta-lbl\">Requester</p><p class=\"meta-val\">{html.escape(req_name)}</p></div>"
            f"<div><p class=\"meta-lbl\">Department</p><p class=\"meta-val\">{html.escape(department_label(ticket))}</p></div>"
            f"<div><p class=\"meta-lbl\">Assignee</p><p class=\"meta-val\">{html.escape(assignee_name(session, ticket))}</p></div>"
            f"<div><p class=\"meta-lbl\">Routing</p><p class=\"meta-val\">{html.escape(hand_routing_label(ticket))}</p></div>"
            f"<div><p class=\"meta-lbl\">Confidence</p><p class=\"meta-val\">{html.escape(confidence)}</p></div>"
            f"<div><p class=\"meta-lbl\">Priority</p><p class=\"meta-val\">{html.escape(ticket.priority or '—')}</p></div>"
            f'<div><p class="meta-lbl">SLA</p><p class="meta-val {sla_cls}">{html.escape(sla_txt)}</p></div>'
            f"<div><p class=\"meta-lbl\">Created</p><p class=\"meta-val\">"
            f"{ticket.created_at.strftime('%Y-%m-%d %H:%M') if ticket.created_at else '—'}</p></div>"
            f"</div></div>"
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _wrap(
            '<div class="admin-card">'
            '<h3>Incident description</h3>'
            f'<p class="admin-ticket-desc">{html.escape(ticket.description_sanitized or ticket.description_raw)}</p>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if clf:
        st.markdown(
            _wrap(
                f'<div class="admin-card"><h3>Classification</h3>'
                f"<p>{html.escape(clf.use_case_category)}"
                f"{f' · {html.escape(clf.subcategory)}' if clf.subcategory else ''}"
                f" · source {html.escape(clf.source or '—')}</p></div>"
            ),
            unsafe_allow_html=True,
        )

    if res and ticket.hand in ("1", "2"):
        steps, _ = decode_steps(res.steps_json)
        if steps:
            step_items = "".join(
                f"<li>{html.escape(s)}</li>" for s in steps
            )
            st.markdown(
                _wrap(
                    f'<div class="admin-card"><h3>Resolution steps</h3>'
                    f"<ol class='admin-resolution-steps'>{step_items}</ol></div>"
                ),
                unsafe_allow_html=True,
            )


def _rag_details_by_ticket(session, ticket_ids: list[str]) -> dict[str, str]:
    if not ticket_ids:
        return {}
    rows = (
        session.query(AuditLog)
        .filter(
            AuditLog.ticket_id.in_(ticket_ids),
            AuditLog.event_type.in_(("rag_hit", "rag_miss")),
        )
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    out: dict[str, str] = {}
    for row in rows:
        out.setdefault(row.ticket_id, row.details or "")
    return out


def _format_confidence_match(ticket: Ticket, rag_details: str | None) -> str:
    conf = f"{ticket.confidence:.0%}" if ticket.confidence is not None else "—"
    if rag_details:
        match = _RAG_DETAIL_RE.search(rag_details)
        if match:
            sim_ref = f"INC-{match.group(1).upper()}"
            sim_score = f"{float(match.group(2)):.0%}"
            return f"{conf} · {sim_ref} ({sim_score})"
    return conf


def _audit_row_data(
    ticket: Ticket,
    stats: AdminDashboardStats,
    rag_details: str | None,
) -> dict[str, Any]:
    return {
        "ticket": ticket,
        "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M") if ticket.created_at else "—",
        "ticket_ref": _ticket_inc(ticket),
        "subject": ticket.title or "—",
        "hand": f"Hand {ticket.hand}" if ticket.hand else "—",
        "confidence_match": _format_confidence_match(ticket, rag_details),
        "team": display_department(ticket.department_queue)
        if ticket.department_queue
        else "—",
        "assignee": _person_name(ticket.assignee_id, stats.assignee_emails),
        "sla": f"{ticket.sla_hours}h" if ticket.sla_hours else "—",
        "priority": ticket.priority or "—",
    }


def _audit_csv(tickets: list[Ticket], stats: AdminDashboardStats, rag_map: dict[str, str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Created",
            "Ticket",
            "Title",
            "Hand",
            "Confidence",
            "Similar Ticket",
            "Team",
            "Assignee",
            "SLA",
            "Priority",
        ]
    )
    for ticket in tickets:
        rag = rag_map.get(ticket.ticket_id)
        conf_match = _format_confidence_match(ticket, rag)
        similar = "—"
        if rag:
            m = _RAG_DETAIL_RE.search(rag)
            if m:
                similar = f"INC-{m.group(1).upper()} ({float(m.group(2)):.0%})"
        writer.writerow(
            [
                ticket.created_at.strftime("%Y-%m-%d %H:%M") if ticket.created_at else "",
                _ticket_inc(ticket),
                ticket.title or "",
                f"Hand {ticket.hand}" if ticket.hand else "",
                f"{ticket.confidence:.0%}" if ticket.confidence is not None else "",
                similar,
                ticket.department_queue or "",
                _person_name(ticket.assignee_id, stats.assignee_emails),
                f"{ticket.sla_hours}h" if ticket.sla_hours else "",
                ticket.priority or "",
            ]
        )
    return buf.getvalue()


def _render_audit(session, stats: AdminDashboardStats) -> None:
    tickets = sorted(stats.all_tickets, key=lambda t: t.created_at or datetime.min, reverse=True)
    rag_map = _rag_details_by_ticket(session, [t.ticket_id for t in tickets])
    _header(
        "Audit Log",
        "Routing decisions at ticket creation — hand, confidence, team, SLA",
        _audit_csv(tickets, stats, rag_map),
    )

    row_data = [_audit_row_data(t, stats, rag_map.get(t.ticket_id)) for t in tickets]
    filtered = _render_filterable_table_shell(
        "Ticket routing audit",
        "audit",
        row_data,
        _AUDIT_COLUMN_FILTERS,
        _AUDIT_COL_WIDTHS,
    )

    def _audit_cells(r: dict[str, Any], t: Ticket) -> str:
        return (
            f"<td>{html.escape(r['created_at'])}</td>"
            f'<td><span class="admin-id">{html.escape(r["ticket_ref"])}</span></td>'
            f'<td class="admin-cell-wrap">{html.escape(r["subject"][:64])}</td>'
            f"<td>{_hand_pill(t.hand)}</td>"
            f'<td class="admin-cell-wrap">{html.escape(r["confidence_match"])}</td>'
            f"<td>{html.escape(r['team'])}</td>"
            f"<td>{html.escape(r['assignee'])}</td>"
            f"<td>{html.escape(r['sla'])}</td>"
            f"<td>{html.escape(r['priority'])}</td>"
        )

    _render_admin_html_table(
        filtered,
        _AUDIT_COL_WIDTHS,
        build_cells=_audit_cells,
        empty_colspan=len(_AUDIT_COLUMN_FILTERS),
    )
    _close_admin_table_panel()


def render_admin_portal(user: User, session) -> None:
    _scope_open()
    if "admin_view" not in st.session_state:
        st.session_state["admin_view"] = "dashboard"

    from src.services.auto_assign_service import run_auto_assignments

    run_auto_assignments(session)
    stats = _cached_admin_stats(session)
    valid_views = {key for key, *_ in _NAV_ITEMS}
    view = st.session_state.get("admin_view", "dashboard")
    if view not in valid_views:
        view = "dashboard"
        st.session_state["admin_view"] = view

    _render_topnav(user)
    detail_id = st.session_state.get("admin_ticket_id")
    if detail_id:
        _render_admin_ticket_detail(user, session, detail_id)
        return

    _render_nav_bar(stats, view)

    if view == "dashboard":
        _render_dashboard(stats)
    elif view == "all_tickets":
        _render_all_tickets(stats)
    elif view == "audit":
        _render_audit(session, stats)
    else:
        _render_dashboard(stats)
