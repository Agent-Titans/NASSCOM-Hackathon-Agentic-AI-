#!/usr/bin/env python3
"""
Master judge test — fresh-machine simulation.

  1. Verify RAG environment (Chroma + syn-* corpus, no live tickets)
  2. Submit diverse new tickets → hand + department
  3. Resolve selected tickets, submit similar follow-ups → compare routing

Usage:
  python scripts/bootstrap_rag_environment.py   # first on a new machine
  python scripts/master_judge_test.py
  python scripts/master_judge_test.py --json report.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.models import (  # noqa: E402
    ClassificationArtifact,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.rag_gate import evaluate_rag_match  # noqa: E402
from src.services.ticket_retrieval import TicketRetrievalService  # noqa: E402
from src.services.ticket_service import TicketService  # noqa: E402
from src.stores.chroma_store import ChromaTicketStore  # noqa: E402
from src.stores.ticket_store import TicketStore  # noqa: E402


@dataclass
class CaseSpec:
    case_id: str
    title: str
    description: str
    expected_hand: str
    expected_department: str
    expected_category: Optional[str] = None
    urgency: str = "medium"
    acceptable_hands: Optional[tuple[str, ...]] = None
    notes: str = ""


@dataclass
class CaseResult:
    case_id: str
    title: str
    expected_hand: str
    expected_department: str
    actual_hand: str
    actual_department: str
    actual_category: str
    status: str
    rag_trusted: bool
    rag_match_id: Optional[str]
    rag_score: Optional[float]
    rag_reason: str
    steps_count: int
    low_grounding: bool
    matched_ticket_id: Optional[str]
    latency_sec: float
    hand_ok: bool
    department_ok: bool
    expected_category: Optional[str] = None
    category_ok: bool = True
    notes: str = ""

    @property
    def passed(self) -> bool:
        return self.hand_ok and self.department_ok and (
            not self.expected_category or self.category_ok
        )


@dataclass
class SimilarPairResult:
    pair_id: str
    original_case_id: str
    followup_case_id: str
    original_hand: str
    followup_hand: str
    original_department: str
    followup_department: str
    hand_consistent: bool
    department_consistent: bool
    followup_rag_match: Optional[str]
    followup_rag_score: Optional[float]
    notes: str = ""


@dataclass
class EscalationResult:
    case_id: str
    before_hand: str
    after_hand: str
    department: str
    assignee_set: bool
    passed: bool


@dataclass
class MasterReport:
    started_at: str
    environment: dict[str, Any]
    phase1_results: list[CaseResult] = field(default_factory=list)
    phase2_extended: list[CaseResult] = field(default_factory=list)
    resolve_ids: list[str] = field(default_factory=list)
    phase3_results: list[CaseResult] = field(default_factory=list)
    phase4_golden: list[CaseResult] = field(default_factory=list)
    phase5_escalation: list[EscalationResult] = field(default_factory=list)
    similar_pairs: list[SimilarPairResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        p1 = self.phase1_results
        p2 = self.phase2_extended
        p3 = self.phase3_results
        p4 = self.phase4_golden
        all_cases = p1 + p2 + p3 + p4
        return {
            "phase1_total": len(p1),
            "phase1_pass": sum(1 for r in p1 if r.passed),
            "phase2_total": len(p2),
            "phase2_pass": sum(1 for r in p2 if r.passed),
            "phase3_total": len(p3),
            "phase3_pass": sum(1 for r in p3 if r.passed),
            "phase4_total": len(p4),
            "phase4_pass": sum(1 for r in p4 if r.passed),
            "phase5_escalation_pass": sum(1 for e in self.phase5_escalation if e.passed),
            "phase5_escalation_total": len(self.phase5_escalation),
            "similar_pairs": len(self.similar_pairs),
            "similar_consistent": sum(
                1 for p in self.similar_pairs if p.hand_consistent and p.department_consistent
            ),
            "overall_pass_rate": (
                sum(1 for r in all_cases if r.passed) / len(all_cases) if all_cases else 0.0
            ),
        }


PHASE1_CASES: list[CaseSpec] = [
    CaseSpec(
        "P1-password",
        "Forgot password",
        "I forgot my password and cannot login to the company portal",
        "1",
        "Access Management",
        "Access Management",
        notes="Classic H1 self-help",
    ),
    CaseSpec(
        "P1-printer",
        "Printer paper jam",
        "The office printer has a paper jam and will not print my documents",
        "1",
        "Hardware",
        "Infrastructure",
        notes="H1 or H2 acceptable; dept Hardware",
    ),
    CaseSpec(
        "P1-security",
        "AWS key exposed",
        "AWS secret access key was accidentally pushed to a public GitHub repository",
        "3",
        "SecOps",
        "Security",
        notes="Always H3 specialist",
    ),
    CaseSpec(
        "P1-vpn",
        "VPN error 807",
        "I'm getting Error 807 when I try to start my VPN client and cannot connect",
        "1",
        "Network",
        "Network",
        acceptable_hands=("1", "2"),
        notes="Golden set: H1 when RAG has VPN playbook",
    ),
    CaseSpec(
        "P1-cognos",
        "Cognos DB configuration",
        "[Other] Need help configuring DB2 connection details for IBM Cognos framework manager",
        "2",
        "DBA",
        "Database",
        notes="DBA queue",
    ),
    CaseSpec(
        "P1-vague",
        "Laptop feels slow",
        "My laptop has been very slow lately and applications take forever to open",
        "2",
        "Hardware",
        notes="Weak RAG → team assist",
    ),
    CaseSpec(
        "P1-docker",
        "Docker hypervisor failure",
        "Docker Desktop fails to start after recent security policy updates on Windows hypervisor",
        "2",
        "Hardware",
        "Infrastructure",
        notes="Infrastructure → Hardware; must NOT be SecOps",
    ),
    CaseSpec(
        "P1-mfa",
        "MFA token not working",
        "My authenticator app MFA code is not working when I try to sign in",
        "1",
        "Access Management",
        "Access Management",
        notes="Access self-help candidate",
    ),
]

PHASE3_FOLLOWUPS: list[tuple[str, CaseSpec]] = [
    (
        "P1-password",
        CaseSpec(
            "P3-password-similar",
            "Password lockout again",
            "I cannot login again — forgot my password for the corporate portal",
            "1",
            "Access Management",
            "Access Management",
            notes="Similar to resolved password ticket",
        ),
    ),
    (
        "P1-printer",
        CaseSpec(
            "P3-printer-similar",
            "Printer jammed again",
            "Paper is stuck in the printer on floor 3 and nothing will print",
            "1",
            "Hardware",
            "Infrastructure",
            notes="Similar to resolved printer ticket",
        ),
    ),
    (
        "P1-security",
        CaseSpec(
            "P3-security-similar",
            "Credential leak on GitHub",
            "Found an API key committed to a public GitHub repo — possible credential leak",
            "3",
            "SecOps",
            "Security",
            notes="Similar security incident",
        ),
    ),
    (
        "P1-vpn",
        CaseSpec(
            "P3-vpn-similar",
            "VPN won't connect",
            "VPN client shows error 807 and I cannot connect to corporate network",
            "1",
            "Network",
            "Network",
            acceptable_hands=("1", "2"),
            notes="Similar VPN issue",
        ),
    ),
]

PHASE2_EXTENDED: list[CaseSpec] = [
    CaseSpec(
        "P2-chrome",
        "Chrome slow",
        "Google Chrome spins forever on any website. Other apps have internet after Windows update.",
        "1",
        "Software",
        "Application",
        notes="App self-help",
    ),
    CaseSpec(
        "P2-charger",
        "Charger not working",
        "Laptop charger not charging, no light on power adapter",
        "2",
        "Hardware",
        "Infrastructure",
        acceptable_hands=("1", "2"),
    ),
    CaseSpec(
        "P2-sql-null",
        "SQL null values",
        "SQL query returns null values in production database table after migration",
        "2",
        "DBA",
        "Database",
    ),
    CaseSpec(
        "P2-nas",
        "NAS backup failed",
        "Storage backup failed last night — NAS share quota may be full",
        "1",
        "DBA",
        "Storage",
        acceptable_hands=("1", "2"),
    ),
    CaseSpec(
        "P2-ip-whitelist",
        "IP whitelist for SQL",
        "I need someone to whitelist my IP so I can reach the SQL database server",
        "2",
        "Network",
        "Network",
    ),
    CaseSpec(
        "P2-outlook",
        "Outlook crash",
        "Microsoft Outlook crashes on startup with error code after latest Office patch",
        "1",
        "Software",
        "Application",
        acceptable_hands=("1", "2"),
    ),
    CaseSpec(
        "P2-sharepoint",
        "SharePoint upload",
        "SharePoint upload fails with permission denied on team site",
        "2",
        "DBA",
        "Storage",
    ),
    CaseSpec(
        "P2-fan",
        "Laptop fan noise",
        "Laptop fan loud after update, overheating on company laptop",
        "2",
        "Hardware",
        "Infrastructure",
    ),
    CaseSpec(
        "P2-phishing",
        "Suspicious email",
        "Received phishing email with malware attachment — clicked suspicious link",
        "3",
        "SecOps",
        "Security",
        urgency="high",
    ),
    CaseSpec(
        "P2-oracle",
        "Oracle deadlock",
        "Oracle database deadlock error ORA-00060 during batch job overnight",
        "2",
        "DBA",
        "Database",
    ),
    CaseSpec(
        "P2-wifi",
        "WiFi certificate",
        "Corporate WiFi prompts untrusted certificate warning on floor 5",
        "2",
        "Network",
        "Network",
        acceptable_hands=("1", "2"),
    ),
    CaseSpec(
        "P2-nonsense",
        "Purple keyboard",
        "The quantum flux capacitor on my keyboard is oscillating at 42 hertz",
        "2",
        "Software",
        notes="Nonsense — should still route somewhere",
    ),
]

GOLDEN_PATH = ROOT / "data" / "golden_tickets.json"

RESOLVE_AFTER_PHASE1 = frozenset({"P1-password", "P1-printer", "P1-vpn"})


def _load_golden_cases() -> list[CaseSpec]:
    if not GOLDEN_PATH.is_file():
        return []
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    out: list[CaseSpec] = []
    for row in data.get("cases", []):
        exp = row.get("expect", {})
        out.append(
            CaseSpec(
                case_id=f"G-{row['id']}",
                title=row["title"],
                description=row["description"],
                expected_hand=str(exp.get("hand", "2")),
                expected_department=str(exp.get("department", "Software")),
                expected_category=str(exp.get("category")) if exp.get("category") else None,
                urgency=row.get("urgency", "medium"),
                notes="golden_set",
            )
        )
    return out


def _hand_matches(spec: CaseSpec, hand: str, dept: str) -> bool:
    if spec.acceptable_hands:
        return hand in spec.acceptable_hands and dept == spec.expected_department
    if spec.case_id in ("P1-printer",) or spec.case_id.startswith("P3-printer"):
        return hand in ("1", "2") and dept == "Hardware"
    return hand == spec.expected_hand


def _get_requester(session) -> User:
    user = session.query(User).filter(User.email == "pallavi@user").first()
    if not user:
        user = session.query(User).filter(User.role == "requester").first()
    if not user:
        raise RuntimeError("No requester user — run scripts/seed_users.py")
    return user


def _check_environment(session) -> dict[str, Any]:
    chroma = ChromaTicketStore()
    live = (
        session.query(Ticket)
        .filter(~Ticket.ticket_id.like("syn-%"))
        .count()
    )
    syn = session.query(Ticket).filter(Ticket.ticket_id.like("syn-%")).count()
    from src.config.settings import get_settings

    settings = get_settings()
    return {
        "chroma_docs": chroma.count,
        "chroma_mode": chroma._embedding_mode,
        "sqlite_syn_resolved": syn,
        "live_ui_tickets": live,
        "rag_corpus_mode": settings.rag_corpus_mode,
        "rag_embedding_backend": settings.rag_embedding_backend,
        "gemini_configured": bool(settings.google_api_key),
    }


def _process_case(session, requester: User, spec: CaseSpec) -> tuple[Ticket, CaseResult]:
    store = TicketStore(session)
    svc = TicketService(session)
    ticket = store.create(requester, spec.title, spec.description, spec.urgency)

    t0 = time.perf_counter()
    with patch.object(svc.guardrail.gemini, "scan_prompt_injection", return_value="SECURITY_OK"):
        result = svc.process_ticket(ticket)
    elapsed = time.perf_counter() - t0

    session.refresh(ticket)
    clf = (
        session.query(ClassificationArtifact)
        .filter_by(ticket_id=ticket.ticket_id)
        .first()
    )
    res = (
        session.query(ResolutionArtifact)
        .filter_by(ticket_id=ticket.ticket_id)
        .first()
    )

    retrieval_text = f"{ticket.title}\n{ticket.description_sanitized or ticket.description_raw}"
    raw = TicketRetrievalService().find_similar(session, retrieval_text)
    gate = evaluate_rag_match(raw, query_text=retrieval_text)

    category = clf.use_case_category if clf else "?"
    steps = json.loads(res.steps_json or "[]") if res else []
    if isinstance(steps, dict):
        steps = steps.get("requester") or steps.get("assignee") or []

    hand = ticket.hand or "?"
    dept = ticket.department_queue or "?"
    hand_ok = _hand_matches(spec, hand, dept)
    dept_ok = dept == spec.expected_department
    category_ok = (not spec.expected_category) or category == spec.expected_category

    cr = CaseResult(
        case_id=spec.case_id,
        title=spec.title,
        expected_hand=spec.expected_hand,
        expected_department=spec.expected_department,
        expected_category=spec.expected_category,
        actual_hand=hand,
        actual_department=dept,
        actual_category=category,
        status=ticket.status or "?",
        rag_trusted=gate.trusted is not None,
        rag_match_id=gate.raw.ticket_id if gate.raw else None,
        rag_score=round(gate.raw.similarity_score, 3) if gate.raw else None,
        rag_reason=gate.reason,
        steps_count=len(steps) if isinstance(steps, list) else 0,
        low_grounding=bool(res.low_grounding) if res else True,
        matched_ticket_id=(
            result.resolution.matched_ticket_id
            if result.resolution
            else None
        ),
        latency_sec=round(elapsed, 2),
        hand_ok=hand_ok,
        department_ok=dept_ok,
        category_ok=category_ok,
        notes=spec.notes,
    )
    return ticket, cr


def _resolve_ticket(session, ticket: Ticket, *, feedback: str = "agent") -> None:
    store = TicketStore(session)
    if ticket.hand == "1" and feedback == "worked":
        store.resolve(ticket)
    else:
        store.resolve(ticket)


def _clear_live_tickets(session) -> int:
    """Remove UI-submitted tickets; keep syn-* RAG history."""
    from src.db.models import (
        AgentRun,
        AuditLog,
        ClassificationArtifact,
        Feedback,
        ResolutionArtifact,
        TicketComment,
    )

    live_ids = [
        tid
        for (tid,) in session.query(Ticket.ticket_id).filter(~Ticket.ticket_id.like("syn-%")).all()
    ]
    if not live_ids:
        return 0
    for model, col in (
        (AuditLog, AuditLog.ticket_id),
        (TicketComment, TicketComment.ticket_id),
        (Feedback, Feedback.ticket_id),
        (AgentRun, AgentRun.ticket_id),
        (ClassificationArtifact, ClassificationArtifact.ticket_id),
        (ResolutionArtifact, ResolutionArtifact.ticket_id),
    ):
        session.query(model).filter(col.in_(live_ids)).delete(synchronize_session=False)
    deleted = (
        session.query(Ticket)
        .filter(Ticket.ticket_id.in_(live_ids))
        .delete(synchronize_session=False)
    )
    session.commit()
    return deleted


def run_master_test() -> MasterReport:
    init_db()
    Session = get_session_factory()
    report = MasterReport(started_at=datetime.now(timezone.utc).isoformat(), environment={})

    with Session() as session:
        cleared = _clear_live_tickets(session)
        if cleared:
            print(f"Cleared {cleared} prior live ticket(s) for fresh judge run.\n")
        report.environment = _check_environment(session)
        requester = _get_requester(session)

        ticket_by_case: dict[str, Ticket] = {}
        result_by_case: dict[str, CaseResult] = {}

        print("\n=== PHASE 1: Fresh tickets (judge scenarios) ===\n")
        for spec in PHASE1_CASES:
            try:
                ticket, cr = _process_case(session, requester, spec)
                ticket_by_case[spec.case_id] = ticket
                result_by_case[spec.case_id] = cr
                report.phase1_results.append(cr)
                mark = "PASS" if cr.passed else "FAIL"
                print(
                    f"  [{mark}] {spec.case_id}: hand={cr.actual_hand} "
                    f"dept={cr.actual_department} cat={cr.actual_category} "
                    f"rag={cr.rag_match_id} ({cr.rag_score}) {cr.latency_sec}s"
                )
            except Exception as exc:
                report.errors.append(f"{spec.case_id}: {exc}")
                print(f"  [ERROR] {spec.case_id}: {exc}")

        print("\n=== PHASE 2: Extended coverage (all departments) ===\n")
        for spec in PHASE2_EXTENDED:
            try:
                ticket, cr = _process_case(session, requester, spec)
                report.phase2_extended.append(cr)
                mark = "PASS" if cr.passed else "FAIL"
                print(
                    f"  [{mark}] {spec.case_id}: hand={cr.actual_hand} "
                    f"dept={cr.actual_department} cat={cr.actual_category} "
                    f"rag={cr.rag_match_id} ({cr.rag_score}) {cr.latency_sec}s"
                )
            except Exception as exc:
                report.errors.append(f"{spec.case_id}: {exc}")
                print(f"  [ERROR] {spec.case_id}: {exc}")

        print("\n=== PHASE 3: Resolve tickets (build live RAG history) ===\n")
        for case_id in RESOLVE_AFTER_PHASE1:
            ticket = ticket_by_case.get(case_id)
            if not ticket:
                continue
            try:
                _resolve_ticket(session, ticket)
                report.resolve_ids.append(ticket.ticket_id)
                print(f"  Resolved {case_id} → {ticket.ticket_id} (hand was {ticket.hand})")
            except Exception as exc:
                report.errors.append(f"resolve {case_id}: {exc}")

        chroma_after = ChromaTicketStore().count
        report.environment["chroma_docs_after_resolve"] = chroma_after
        report.environment["resolved_for_rag"] = list(report.resolve_ids)

        print("\n=== PHASE 4: Similar follow-up tickets ===\n")
        for orig_id, spec in PHASE3_FOLLOWUPS:
            try:
                ticket, cr = _process_case(session, requester, spec)
                report.phase3_results.append(cr)
                orig = result_by_case.get(orig_id)
                if orig:
                    pair = SimilarPairResult(
                        pair_id=f"{orig_id}→{spec.case_id}",
                        original_case_id=orig_id,
                        followup_case_id=spec.case_id,
                        original_hand=orig.actual_hand,
                        followup_hand=cr.actual_hand,
                        original_department=orig.actual_department,
                        followup_department=cr.actual_department,
                        hand_consistent=(
                            cr.actual_hand == orig.actual_hand
                            or (
                                orig.case_id in ("P1-printer",)
                                and cr.actual_hand in ("1", "2")
                                and orig.actual_hand in ("1", "2")
                            )
                        ),
                        department_consistent=cr.actual_department == orig.actual_department,
                        followup_rag_match=cr.rag_match_id,
                        followup_rag_score=cr.rag_score,
                        notes=spec.notes,
                    )
                    report.similar_pairs.append(pair)
                mark = "PASS" if cr.passed else "FAIL"
                consist = ""
                if report.similar_pairs:
                    p = report.similar_pairs[-1]
                    consist = f" consistent={p.hand_consistent and p.department_consistent}"
                print(
                    f"  [{mark}] {spec.case_id}: hand={cr.actual_hand} "
                    f"dept={cr.actual_department} rag={cr.rag_match_id}{consist}"
                )
            except Exception as exc:
                report.errors.append(f"{spec.case_id}: {exc}")
                print(f"  [ERROR] {spec.case_id}: {exc}")

        golden_cases = _load_golden_cases()
        print(f"\n=== PHASE 5: Golden set ({len(golden_cases)} cases) ===\n")
        for spec in golden_cases:
            try:
                _ticket, cr = _process_case(session, requester, spec)
                report.phase4_golden.append(cr)
                mark = "PASS" if cr.passed else "FAIL"
                print(
                    f"  [{mark}] {spec.case_id}: hand={cr.actual_hand} "
                    f"dept={cr.actual_department} cat={cr.actual_category}"
                )
            except Exception as exc:
                report.errors.append(f"{spec.case_id}: {exc}")
                print(f"  [ERROR] {spec.case_id}: {exc}")

        print("\n=== PHASE 6: H1 'Did not work' escalation ===\n")
        from src.services.auto_assign_service import assign_escalated_ticket
        from src.stores.audit_store import AuditLogStore

        esc_ticket, esc_cr = _process_case(
            session,
            requester,
            CaseSpec(
                "P6-h1-escalate",
                "Portal password reset",
                "I forgot my password and cannot login to the company portal",
                "1",
                "Access Management",
                "Access Management",
            ),
        )
        before_hand = esc_ticket.hand
        store = TicketStore(session)
        store.update_hand(
            esc_ticket,
            hand="2",
            confidence=esc_ticket.confidence or 0.5,
            status="ROUTED",
            department_queue=esc_ticket.department_queue,
            priority=esc_ticket.priority,
            sla_hours=esc_ticket.sla_hours,
            escalation_required=False,
        )
        AuditLogStore(session).record(
            esc_ticket, "feedback_escalation", details="outcome=failed hand=1_to_2"
        )
        session.commit()
        assigned = assign_escalated_ticket(session, esc_ticket)
        session.refresh(esc_ticket)
        esc = EscalationResult(
            case_id="P6-h1-escalate",
            before_hand=before_hand or "?",
            after_hand=esc_ticket.hand or "?",
            department=esc_ticket.department_queue or "?",
            assignee_set=bool(esc_ticket.assignee_id),
            passed=(
                before_hand == "1"
                and esc_ticket.hand == "2"
                and esc_ticket.department_queue == "Access Management"
                and assigned
            ),
        )
        report.phase5_escalation.append(esc)
        mark = "PASS" if esc.passed else "FAIL"
        print(
            f"  [{mark}] H1→H2 dept={esc.department} assignee={esc.assignee_set} "
            f"(before={esc.before_hand} after={esc.after_hand})"
        )

    return report


def _markdown_report(report: MasterReport) -> str:
    env = report.environment
    s = report.summary()
    lines = [
        "# Master Judge Test Report",
        "",
        f"**Run at:** {report.started_at}",
        "",
        "## Environment (fresh machine check)",
        "",
        f"| Check | Value |",
        f"|-------|-------|",
        f"| Chroma documents | {env.get('chroma_docs', '?')} |",
        f"| Chroma embedding mode | {env.get('chroma_mode', '?')} |",
        f"| SQLite syn-* (RAG history) | {env.get('sqlite_syn_resolved', '?')} |",
        f"| Live UI tickets (before test) | {env.get('live_ui_tickets', '?')} |",
        f"| RAG corpus mode | {env.get('rag_corpus_mode', '?')} |",
        f"| Embedding backend | {env.get('rag_embedding_backend', '?')} |",
        f"| Gemini API key set | {env.get('gemini_configured', '?')} |",
        "",
        "## Phase 1 — New ticket routing",
        "",
        f"**Pass rate:** {s['phase1_pass']}/{s['phase1_total']}",
        "",
        "| Case | Expected H/Dept | Actual H/Dept | Category | RAG match | Pass |",
        "|------|-----------------|---------------|----------|-----------|------|",
    ]
    for r in report.phase1_results:
        exp = f"H{r.expected_hand} / {r.expected_department}"
        act = f"H{r.actual_hand} / {r.actual_department}"
        rag = f"{r.rag_match_id or '—'} ({r.rag_score or '—'})"
        ok = "✓" if r.passed else "✗"
        lines.append(
            f"| {r.case_id} | {exp} | {act} | {r.actual_category} | {rag} | {ok} |"
        )

    lines.extend(
        [
            "",
            f"## Phase 2 — Extended coverage ({s['phase2_pass']}/{s['phase2_total']})",
            "",
            "| Case | Expected | Actual | Category | Pass |",
            "|------|----------|--------|----------|------|",
        ]
    )
    for r in report.phase2_extended:
        exp = f"H{r.expected_hand} / {r.expected_department}"
        act = f"H{r.actual_hand} / {r.actual_department}"
        ok = "✓" if r.passed else "✗"
        lines.append(f"| {r.case_id} | {exp} | {act} | {r.actual_category} | {ok} |")

    lines.extend(["", "## Phase 3 — Resolved tickets", ""])
    for tid in report.resolve_ids:
        lines.append(f"- `{tid}`")

    lines.extend(
        [
            "",
            f"## Phase 4 — Similar follow-ups ({s['phase3_pass']}/{s['phase3_total']})",
            "",
            "| Case | Expected | Actual | Consistent |",
            "|------|----------|--------|------------|",
        ]
    )
    for r in report.phase3_results:
        exp = f"H{r.expected_hand} / {r.expected_department}"
        act = f"H{r.actual_hand} / {r.actual_department}"
        pair = next((p for p in report.similar_pairs if p.followup_case_id == r.case_id), None)
        cons = "✓" if pair and pair.hand_consistent and pair.department_consistent else "✗"
        lines.append(f"| {r.case_id} | {exp} | {act} | {cons} |")

    lines.extend(
        [
            "",
            f"## Phase 5 — Golden set ({s['phase4_pass']}/{s['phase4_total']})",
            "",
            "| Case | Expected | Actual | Pass |",
            "|------|----------|--------|------|",
        ]
    )
    for r in report.phase4_golden:
        exp = f"H{r.expected_hand} / {r.expected_department} / {r.expected_category or '—'}"
        act = f"H{r.actual_hand} / {r.actual_department} / {r.actual_category}"
        ok = "✓" if r.passed else "✗"
        lines.append(f"| {r.case_id} | {exp} | {act} | {ok} |")

    lines.extend(
        [
            "",
            f"## Phase 6 — H1 escalation ({s['phase5_escalation_pass']}/{s['phase5_escalation_total']})",
            "",
        ]
    )
    for e in report.phase5_escalation:
        ok = "✓" if e.passed else "✗"
        lines.append(
            f"- {ok} {e.case_id}: H{e.before_hand}→H{e.after_hand} "
            f"dept={e.department} assignee={e.assignee_set}"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **Overall pass rate (P1+P2+P4+P5):** {s['overall_pass_rate']:.0%}",
            f"- **Phase 1:** {s['phase1_pass']}/{s['phase1_total']}",
            f"- **Phase 2 extended:** {s['phase2_pass']}/{s['phase2_total']}",
            f"- **Phase 4 similar:** {s['phase3_pass']}/{s['phase3_total']} "
            f"(consistent {s['similar_consistent']}/{s['similar_pairs']})",
            f"- **Golden set:** {s['phase4_pass']}/{s['phase4_total']}",
        ]
    )
    if report.errors:
        lines.extend(["", "## Errors", ""])
        for e in report.errors:
            lines.append(f"- {e}")

    verdict = (
        "PASS"
        if s["overall_pass_rate"] >= 0.82
        and s["similar_consistent"] >= max(1, s["similar_pairs"] - 1)
        and s.get("phase5_escalation_pass", 0) >= 1
        else "REVIEW"
    )
    lines.extend(["", f"## Verdict: **{verdict}**", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Master judge routing test")
    parser.add_argument("--json", type=Path, help="Write JSON report")
    parser.add_argument("--md", type=Path, help="Write Markdown report")
    args = parser.parse_args()

    report = run_master_test()
    md = _markdown_report(report)
    print("\n" + "=" * 60)
    print(md)

    if args.json:
        payload = {
            "started_at": report.started_at,
            "environment": report.environment,
            "summary": report.summary(),
            "phase1": [asdict(r) for r in report.phase1_results],
            "phase2_extended": [asdict(r) for r in report.phase2_extended],
            "phase3_followups": [asdict(r) for r in report.phase3_results],
            "phase4_golden": [asdict(r) for r in report.phase4_golden],
            "phase5_escalation": [asdict(e) for e in report.phase5_escalation],
            "similar_pairs": [asdict(p) for p in report.similar_pairs],
            "resolve_ids": report.resolve_ids,
            "errors": report.errors,
        }
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote {args.json}")

    out_md = args.md or ROOT / "docs" / "MASTER_JUDGE_REPORT.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md}")

    s = report.summary()
    return 0 if s["overall_pass_rate"] >= 0.75 and not report.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
