#!/usr/bin/env python3
"""Smoke-test all portal pages via Streamlit AppTest."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

from src.db.session import get_session_factory, init_db
from src.db.models import Ticket, User
from src.config.departments import departments_match


def _set(at: AppTest, **kwargs) -> None:
    for key, value in kwargs.items():
        at.session_state[key] = value


def _login(at: AppTest, email: str) -> User:
    init_db()
    with get_session_factory()() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            raise RuntimeError(f"Missing seed user {email}")
        at.session_state["user"] = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "department": user.department,
        }
        at.session_state["signed_in"] = True
        return user


def _first_ticket_for(user: User) -> str | None:
    with get_session_factory()() as session:
        t = (
            session.query(Ticket)
            .filter_by(user_id=user.user_id)
            .order_by(Ticket.created_at.desc())
            .first()
        )
        return t.ticket_id if t else None


def _ensure_requester_ticket(user: User) -> str:
    tid = _first_ticket_for(user)
    if tid:
        return tid
    from src.services.ticket_service import TicketService
    from src.stores.ticket_store import TicketStore

    with get_session_factory()() as session:
        u = session.get(User, user.user_id)
        ticket = TicketStore(session).create(
            u, "UI smoke ticket", "Automated UI smoke test incident.", "medium"
        )
        TicketService(session).process_ticket(ticket)
        session.commit()
        return ticket.ticket_id


def _dept_ticket(dept: str) -> str | None:
    with get_session_factory()() as session:
        t = (
            session.query(Ticket)
            .filter(Ticket.department_queue == dept, Ticket.hand.in_(("2", "3")))
            .order_by(Ticket.created_at.desc())
            .first()
        )
        return t.ticket_id if t else None


def _ensure_specialists_ticket() -> str:
    from src.config.specialists import SPECIALISTS_QUEUE, STATUS_ROUTING_REVIEW
    from src.services.specialists_desk_service import request_specialist_review

    with get_session_factory()() as session:
        t = (
            session.query(Ticket)
            .filter_by(department_queue=SPECIALISTS_QUEUE)
            .order_by(Ticket.created_at.desc())
            .first()
        )
        if t:
            t.assignee_id = None
            if t.status in ("RESOLVED", "CLOSED"):
                t.status = STATUS_ROUTING_REVIEW
            session.commit()
            return t.ticket_id

        requester = session.query(User).filter_by(email="pallavi@user").first()
        app_agent = session.query(User).filter_by(email="subbu@employee").first()
        if not requester or not app_agent:
            raise RuntimeError("Missing seed users for specialists ticket")
        from src.services.ticket_service import TicketService
        from src.stores.ticket_store import TicketStore

        ticket = TicketStore(session).create(
            requester,
            "UI smoke specialists ticket",
            "Automated SecOps routing desk smoke test.",
            "high",
        )
        TicketService(session).process_ticket(ticket)
        session.commit()
        session.refresh(ticket)
        if ticket.department_queue != "Application":
            ticket.department_queue = "Application"
            ticket.hand = "2"
            ticket.status = "ROUTED"
            session.commit()
        ok, msg = request_specialist_review(
            session,
            ticket,
            app_agent,
            "Misrouted to Application — needs SecOps routing specialist review.",
        )
        if not ok:
            raise RuntimeError(msg)
        session.commit()
        return ticket.ticket_id


def _ensure_agent_detail_ticket(user: User) -> str:
    """Application/SecOps H2 ticket that renders agent detail (Back + Route buttons)."""
    from src.config.specialists import SPECIALISTS_QUEUE

    dept = user.department or "Application"
    _ensure_routable_app_ticket()
    with get_session_factory()() as session:
        t = (
            session.query(Ticket)
            .filter(
                Ticket.department_queue == dept,
                Ticket.hand.in_(("2", "3")),
                Ticket.status.notin_(("RESOLVED", "CLOSED")),
                Ticket.department_queue != SPECIALISTS_QUEUE,
            )
            .order_by(Ticket.created_at.desc())
            .first()
        )
        if t:
            t.assignee_id = None
            t.hand = "2" if t.hand not in ("2", "3") else t.hand
            t.status = "ROUTED" if t.status in ("RESOLVED", "CLOSED") else t.status
            session.commit()
            return t.ticket_id
    return _ensure_dept_ticket(dept, user)


def _ensure_dept_ticket(dept: str, user: User) -> str:
    tid = _dept_ticket(dept)
    if tid:
        with get_session_factory()() as session:
            ticket = session.get(Ticket, tid)
            if ticket:
                ticket.assignee_id = None
                if ticket.status in ("RESOLVED", "CLOSED"):
                    ticket.status = "ROUTED"
                session.commit()
        return tid
    from src.services.ticket_service import TicketService
    from src.stores.ticket_store import TicketStore

    with get_session_factory()() as session:
        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            raise RuntimeError("Missing pallavi@user for dept ticket seed")
        ticket = TicketStore(session).create(
            requester,
            f"UI smoke {dept} ticket",
            "Automated agent UI smoke test incident.",
            "high",
        )
        result = TicketService(session).process_ticket(ticket)
        session.commit()
        session.refresh(ticket)
        if not departments_match(ticket.department_queue, dept):
            ticket.department_queue = dept
            ticket.hand = "2"
            ticket.status = "ROUTED"
            ticket.assignee_id = None
            session.commit()
        return ticket.ticket_id


def _ensure_routable_app_ticket() -> None:
    """Ensure an open Application H2 ticket exists that subbu can Route."""
    from src.services.specialists_desk_service import can_request_specialist

    with get_session_factory()() as session:
        agent = session.query(User).filter_by(email="subbu@employee").first()
        if not agent:
            return
        open_app = (
            session.query(Ticket)
            .filter(
                Ticket.department_queue == "Application",
                Ticket.hand.in_(("2", "3")),
                Ticket.status.notin_(("RESOLVED", "CLOSED")),
            )
            .all()
        )
        if any(can_request_specialist(t, agent) for t in open_app):
            return
        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            return
        from src.stores.ticket_store import TicketStore

        ticket = TicketStore(session).create(
            requester,
            "QA routable Application ticket",
            "Application crash on launch — needs department review.",
            "medium",
        )
        ticket.department_queue = "Application"
        ticket.hand = "2"
        ticket.status = "ROUTED"
        ticket.assignee_id = None
        session.commit()


def _ensure_secops_ops_ticket() -> str:
    with get_session_factory()() as session:
        t = (
            session.query(Ticket)
            .filter_by(department_queue="SecOps", hand="3")
            .order_by(Ticket.created_at.desc())
            .first()
        )
        if t:
            t.assignee_id = None
            if t.status in ("RESOLVED", "CLOSED"):
                t.status = "HUMAN_REVIEW"
            session.commit()
            return t.ticket_id

        requester = session.query(User).filter_by(email="pallavi@user").first()
        if not requester:
            raise RuntimeError("Missing pallavi@user for SecOps ticket seed")
        from src.services.ticket_service import TicketService
        from src.stores.ticket_store import TicketStore

        ticket = TicketStore(session).create(
            requester,
            "UI smoke SecOps H3 ticket",
            "Automated SecOps operational UI smoke test.",
            "high",
        )
        TicketService(session).process_ticket(ticket)
        session.commit()
        session.refresh(ticket)
        ticket.department_queue = "SecOps"
        ticket.hand = "3"
        ticket.status = "HUMAN_REVIEW"
        ticket.assignee_id = None
        session.commit()
        return ticket.ticket_id


def main() -> int:
    app_path = ROOT / "src" / "ui" / "app.py"
    errors: list[str] = []
    _ensure_routable_app_ticket()

    cases = [
        ("employee_home", "pallavi@user", lambda at, u: None),
        (
            "employee_create",
            "pallavi@user",
            lambda at, u: _set(at, portal_view="create", page="portal"),
        ),
        (
            "employee_detail",
            "pallavi@user",
            lambda at, u: _set(
                at,
                portal_view="detail",
                page="portal",
                ticket_id=_ensure_requester_ticket(u),
            ),
        ),
        ("agent_home", "subbu@employee", lambda at, u: None),
        (
            "agent_detail",
            "subbu@employee",
            lambda at, u: _set(
                at,
                agent_view="detail",
                page="agent",
                ticket_id=_ensure_agent_detail_ticket(u),
            ),
        ),
        ("admin_home", "admin@employee", lambda at, u: None),
        (
            "admin_all_tickets",
            "admin@employee",
            lambda at, u: _set(at, admin_view="all_tickets", page="admin"),
        ),
        (
            "admin_audit",
            "admin@employee",
            lambda at, u: _set(at, admin_view="audit", page="admin"),
        ),
        (
            "admin_ticket_detail",
            "admin@employee",
            lambda at, u: _set(
                at,
                admin_view="all_tickets",
                page="admin",
                admin_ticket_id=_ensure_requester_ticket(u),
            ),
        ),
        (
            "secops_specialists_detail",
            "narsimha@employee",
            lambda at, u: _set(
                at,
                agent_view="detail",
                page="agent",
                ticket_id=_ensure_specialists_ticket(),
            ),
        ),
        (
            "secops_regular_detail",
            "narsimha@employee",
            lambda at, u: _set(
                at,
                agent_view="detail",
                page="agent",
                ticket_id=_ensure_secops_ops_ticket(),
            ),
        ),
    ]

    for name, email, setup in cases:
        try:
            at = AppTest.from_file(str(app_path), default_timeout=120)
            user = _login(at, email)
            setup(at, user)
            at.run(timeout=120)
            if at.exception:
                errors.append(f"{name}: {at.exception[0].value}")
                print(f"FAIL {name}: {at.exception[0].value}")
            else:
                labels = [getattr(w, "label", "") or "" for w in at.button]
                print(f"OK   {name}: buttons={len(at.button)} expanders={len(at.expander)}")
                if name == "secops_specialists_detail":
                    if "Confirm route" in labels:
                        errors.append("secops: old Confirm route button present")
                        print("FAIL secops_specialists_detail: Confirm route still present")
                    elif "Route" not in labels:
                        errors.append("secops: missing Route button")
                        print("FAIL secops_specialists_detail: missing Route button")
                    elif len(at.selectbox) < 1:
                        errors.append("secops: missing department selectbox")
                        print("FAIL secops_specialists_detail: missing department selectbox")
                elif name == "secops_regular_detail":
                    if "Route" not in labels:
                        errors.append("secops_regular: missing Route button")
                        print("FAIL secops_regular_detail: missing Route button")
                    elif len(at.selectbox) < 1:
                        errors.append("secops_regular: missing department selectbox")
                        print("FAIL secops_regular_detail: missing department selectbox")
                elif name == "employee_detail" and len(at.expander) < 1:
                    errors.append("employee_detail: missing detail expanders")
                    print("FAIL employee_detail: missing detail expanders")
                elif name == "agent_detail":
                    if "← Back to inbox" in labels:
                        errors.append("agent_detail: Back to inbox should be removed")
                        print("FAIL agent_detail: Back to inbox still present")
                    elif "← Back to dashboard" not in labels:
                        errors.append("agent_detail: missing Back to dashboard")
                        print("FAIL agent_detail: missing Back to dashboard")
                    elif "Route" not in labels:
                        errors.append("agent_detail: missing Route button")
                        print("FAIL agent_detail: missing Route button")
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    # URL restore — employee detail
    try:
        init_db()
        with get_session_factory()() as session:
            pallavi = session.query(User).filter_by(email="pallavi@user").first()
        tid = _ensure_requester_ticket(pallavi) if pallavi else None
        if tid:
            at = AppTest.from_file(str(app_path), default_timeout=120)
            _login(at, "pallavi@user")
            at.query_params["portal_view"] = "detail"
            at.query_params["ticket"] = tid
            at.run(timeout=120)
            if at.exception:
                errors.append(f"employee_url_restore: {at.exception[0].value}")
                print(f"FAIL employee_url_restore: {at.exception[0].value}")
            elif at.session_state["portal_view"] != "detail":
                errors.append("employee_url_restore: view not restored")
                print("FAIL employee_url_restore: view not restored")
            else:
                print("OK   employee_url_restore")
    except Exception as exc:
        errors.append(f"employee_url_restore: {exc}")
        print(f"FAIL employee_url_restore: {exc}")

    # URL restore — agent detail
    try:
        tid = _dept_ticket("Application")
        if tid:
            at = AppTest.from_file(str(app_path), default_timeout=120)
            _login(at, "subbu@employee")
            at.query_params["agent_view"] = "detail"
            at.query_params["ticket"] = tid
            at.run(timeout=120)
            if at.exception:
                errors.append(f"agent_url_restore: {at.exception[0].value}")
                print(f"FAIL agent_url_restore: {at.exception[0].value}")
            elif at.session_state["agent_view"] != "detail":
                errors.append("agent_url_restore: view not restored")
                print("FAIL agent_url_restore: view not restored")
            else:
                print("OK   agent_url_restore")
    except Exception as exc:
        errors.append(f"agent_url_restore: {exc}")
        print(f"FAIL agent_url_restore: {exc}")

    # Extended QA — portal logic without browser
    print("---")
    print("Apple QA (logic checks)")
    try:
        from src.config.departments import CATEGORY_TO_DEPARTMENT, OPERATIONAL_DEPARTMENT_SET
        from src.services.specialists_desk_service import can_request_specialist, is_specialists_ticket
        from src.config.specialists import SPECIALISTS_QUEUE

        if "SecOps" in OPERATIONAL_DEPARTMENT_SET:
            errors.append("qa: SecOps must not be in operational reroute set")
            print("FAIL qa_operational_set")
        else:
            print("OK   qa_operational_set")

        if CATEGORY_TO_DEPARTMENT.get("Security") != "SecOps":
            errors.append("qa: Security must map to SecOps")
            print("FAIL qa_security_map")
        else:
            print("OK   qa_security_map")

        if len(CATEGORY_TO_DEPARTMENT) < 6:
            errors.append("qa: category map incomplete")
            print("FAIL qa_category_count")
        else:
            print("OK   qa_category_count")

        _ensure_routable_app_ticket()
        init_db()
        with get_session_factory()() as session:
            agent = session.query(User).filter_by(email="subbu@employee").first()
            tickets = (
                session.query(Ticket)
                .filter(
                    Ticket.department_queue == "Application",
                    Ticket.hand.in_(("2", "3")),
                    Ticket.status.notin_(("RESOLVED", "CLOSED")),
                )
                .order_by(Ticket.created_at.desc())
                .all()
            )
            routable = [t for t in tickets if agent and can_request_specialist(t, agent)]
            if routable:
                print("OK   qa_can_route")
            elif not tickets:
                print("OK   qa_can_route (no open Application tickets — skipped)")
            else:
                t0 = tickets[0]
                errors.append(
                    f"qa: app agent cannot route ticket hand={t0.hand} status={t0.status}"
                )
                print(f"FAIL qa_can_route (hand={t0.hand} status={t0.status})")

            spec = session.query(Ticket).filter_by(department_queue=SPECIALISTS_QUEUE).first()
            if spec and not is_specialists_ticket(spec):
                errors.append("qa: specialists queue detection")
                print("FAIL qa_specialists_detect")
            else:
                print("OK   qa_specialists_detect")
    except Exception as exc:
        errors.append(f"apple_qa: {exc}")
        print(f"FAIL apple_qa: {exc}")

    print("---")
    if errors:
        print(f"{len(errors)} failure(s)")
        return 1
    print("All UI smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
