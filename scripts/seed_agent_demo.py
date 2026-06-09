#!/usr/bin/env python3
"""Seed department-queue demo tickets for all 7 assignee teams."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.models import (  # noqa: E402
    ClassificationArtifact,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.db.session import get_session_factory, init_db  # noqa: E402

# dept, title, desc, hand, pri, sla_h, status, hours_ago, assignee_email, requester_email
DEMO_TICKETS = [
    (
        "Hardware",
        "Laptop fan running at full speed",
        "MacBook Pro M2 overheating during video calls. Fan noise constant since Monday.",
        "2",
        "P1",
        24,
        "ROUTED",
        6,
        None,
        "emily.reed@demo.local",
    ),
    (
        "Hardware",
        "Docking station not detecting monitors",
        "USB-C dock powers laptop but dual monitors stay black after OS update.",
        "2",
        "P2",
        48,
        "IN_PROGRESS",
        18,
        "hardware@demo.local",
        "james.wu@demo.local",
    ),
    (
        "Hardware",
        "Keyboard keys sticking after spill",
        "Several keys on Dell Latitude sticky after minor coffee spill last week.",
        "2",
        "P2",
        48,
        "ROUTED",
        9,
        None,
        "sarah.kim@demo.local",
    ),
    (
        "Software",
        "CRM export fails with timeout",
        "Exporting >5k rows from Sales CRM times out after 60 seconds.",
        "2",
        "P1",
        24,
        "ROUTED",
        4,
        None,
        "michael.brown@demo.local",
    ),
    (
        "Software",
        "Outlook add-in crashes on launch",
        "Calendar sync add-in crashes immediately after login on Windows 11.",
        "2",
        "P2",
        48,
        "ROUTED",
        12,
        None,
        "requester@demo.local",
    ),
    (
        "Software",
        "Excel macro disabled by policy",
        "Finance team macros blocked after security baseline push.",
        "2",
        "P1",
        24,
        "ROUTED",
        14,
        None,
        "emily.reed@demo.local",
    ),
    (
        "SecOps",
        "Suspicious login from unknown region",
        "Multiple failed MFA attempts followed by success from IP in unfamiliar country.",
        "3",
        "P0",
        4,
        "HUMAN_REVIEW",
        1,
        None,
        "sarah.kim@demo.local",
    ),
    (
        "SecOps",
        "Phishing report — payroll redirect",
        "User forwarded email asking to verify payroll via external link.",
        "3",
        "P0",
        4,
        "IN_PROGRESS",
        2,
        "secops@demo.local",
        "james.wu@demo.local",
    ),
    (
        "SecOps",
        "DLP alert — bulk file download",
        "User downloaded 2,400 files to personal cloud storage in 10 minutes.",
        "3",
        "P0",
        4,
        "ROUTED",
        3,
        None,
        "michael.brown@demo.local",
    ),
    (
        "Network",
        "Cannot connect to VPN from home",
        "VPN client hangs at 'connecting' — works on office Wi-Fi only.",
        "2",
        "P0",
        4,
        "ROUTED",
        3,
        None,
        "requester@demo.local",
    ),
    (
        "Network",
        "Wi-Fi drops every 20 minutes",
        "Corporate SSID disconnects on floor 3; other floors unaffected.",
        "2",
        "P1",
        24,
        "ROUTED",
        8,
        None,
        "emily.reed@demo.local",
    ),
    (
        "Network",
        "DNS resolution slow on guest VLAN",
        "Guest network pages take 8–12s to resolve; corporate VLAN is fine.",
        "2",
        "P2",
        48,
        "ROUTED",
        11,
        None,
        "james.wu@demo.local",
    ),
    (
        "Identity",
        "Password reset link expired",
        "New hire cannot complete SSO enrollment — reset token invalid.",
        "2",
        "P1",
        24,
        "ROUTED",
        5,
        None,
        "sarah.kim@demo.local",
    ),
    (
        "Identity",
        "Okta group membership missing",
        "Finance analyst not in required app group after role change.",
        "2",
        "P2",
        48,
        "IN_PROGRESS",
        20,
        "identity@demo.local",
        "michael.brown@demo.local",
    ),
    (
        "Identity",
        "MFA device lost — locked out",
        "User replaced phone and cannot authenticate to Okta.",
        "2",
        "P0",
        4,
        "ROUTED",
        2,
        None,
        "requester@demo.local",
    ),
    (
        "DBA",
        "Report query running 40+ minutes",
        "Monthly billing report against prod replica blocking other jobs.",
        "2",
        "P0",
        4,
        "ROUTED",
        2,
        None,
        "emily.reed@demo.local",
    ),
    (
        "DBA",
        "Replication lag on analytics cluster",
        "Analytics replica 35 minutes behind primary since maintenance window.",
        "2",
        "P1",
        24,
        "ROUTED",
        10,
        None,
        "james.wu@demo.local",
    ),
    (
        "DBA",
        "Failed index rebuild on staging",
        "Nightly index maintenance failed with deadlock on orders table.",
        "2",
        "P2",
        48,
        "ROUTED",
        16,
        None,
        "sarah.kim@demo.local",
    ),
    (
        "Storage",
        "Shared drive quota exceeded",
        "Marketing share full — team cannot save campaign assets.",
        "2",
        "P1",
        24,
        "ROUTED",
        7,
        None,
        "michael.brown@demo.local",
    ),
    (
        "Storage",
        "Backup job failed — NAS unreachable",
        "Nightly backup to NAS target failed with connection timeout.",
        "2",
        "P2",
        48,
        "IN_PROGRESS",
        15,
        "storage@demo.local",
        "requester@demo.local",
    ),
    (
        "Storage",
        "Archive restore request — legal hold",
        "Legal team needs Q1 mailbox archive restored for litigation review.",
        "2",
        "P1",
        24,
        "ROUTED",
        6,
        None,
        "emily.reed@demo.local",
    ),
]

_CATEGORY_MAP = {
    "Hardware": "Infrastructure",
    "Software": "Application",
    "SecOps": "Security",
    "Network": "Network",
    "Identity": "Access Management",
    "DBA": "Database",
    "Storage": "Storage",
}

_STEPS = {
    "2": [
        "Verify affected configuration and recent changes.",
        "Apply standard runbook steps for this category.",
        "Validate service restoration with the requester.",
    ],
    "3": [
        "Review escalation context and audit trail.",
        "Confirm policy requirements before remediation.",
    ],
}


def main() -> None:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        requesters = {
            u.email: u
            for u in session.query(User).filter(User.role == "requester").all()
        }
        if not requesters:
            print("Run seed_users.py first — no requesters found.")
            return

        assignees = {
            u.email: u
            for u in session.query(User).filter(User.role == "assignee").all()
        }
        existing = {
            (t.department_queue, t.title)
            for t in session.query(Ticket).filter(Ticket.department_queue.isnot(None)).all()
        }

        created = 0
        for row in DEMO_TICKETS:
            (
                dept,
                title,
                desc,
                hand,
                pri,
                sla,
                status,
                hours_ago,
                assignee_email,
                requester_email,
            ) = row
            if (dept, title) in existing:
                continue

            requester = requesters.get(requester_email) or next(iter(requesters.values()))
            assignee = assignees.get(assignee_email) if assignee_email else None
            created_at = datetime.utcnow() - timedelta(hours=hours_ago)
            ticket = Ticket(
                user_id=requester.user_id,
                assignee_id=assignee.user_id if assignee else None,
                title=title,
                description_raw=desc,
                description_sanitized=desc,
                urgency="high" if pri == "P0" else "medium" if pri == "P1" else "low",
                status=status,
                hand=hand,
                confidence=0.72 if hand == "2" else 0.48,
                department_queue=dept,
                priority=pri,
                sla_hours=sla,
                escalation_required=hand == "3",
                created_at=created_at,
                updated_at=created_at,
            )
            session.add(ticket)
            session.flush()

            category = _CATEGORY_MAP.get(dept, "General")
            session.add(
                ClassificationArtifact(
                    ticket_id=ticket.ticket_id,
                    use_case_category=category,
                    subcategory=dept,
                    confidence_hint="medium",
                )
            )
            session.add(
                ResolutionArtifact(
                    ticket_id=ticket.ticket_id,
                    steps_json=json.dumps(_STEPS.get(hand, [])),
                    citations_json=json.dumps([f"KB-{dept[:3].upper()}-001"]),
                    low_grounding=hand == "3",
                    similarity_score=0.74 if hand == "2" else 0.42,
                )
            )
            created += 1

        session.commit()
    print(f"Seeded {created} department demo tickets.")


if __name__ == "__main__":
    main()
