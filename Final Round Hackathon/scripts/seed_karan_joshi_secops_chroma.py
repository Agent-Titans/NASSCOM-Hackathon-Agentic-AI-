"""Seed 50 SecOps ticket documents into ChromaDB and SQLite for Karan Joshi."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from random import choice

from src.config.settings import get_settings
from src.db.models import (
    Base,
    ClassificationArtifact,
    ResolutionArtifact,
    Ticket,
    User,
)
from src.db.session import get_session_factory, init_db
from src.stores.chroma_store import ChromaTicketStore

TITLE_TEMPLATES = [
    "{} detected on {}",
    "{} alert from {}",
    "{} anomaly affecting {}",
    "{} policy violation in {}",
    "{} audit finding for {}",
    "{} incident in {}",
    "{} configuration issue on {}",
    "{} breach attempt via {}",
    "{} access failure for {}",
    "{} data exposure risk from {}",
]

DESCRIPTION_TEMPLATES = [
    "The SecOps team observed a {} affecting {}. The issue includes {} and requires a security review.",
    "Automated monitoring flagged {} for {}. This appears to be caused by {} and impacts security posture.",
    "User activity indicates {} on {}. Recommend investigating {} and applying SecOps remediation.",
    "A critical {} event was logged involving {}. Initial triage shows {} and escalation to SecOps is needed.",
]

CONTEXTS = [
    "remote VPN access",
    "corporate cloud instance",
    "identity provider integration",
    "privileged admin session",
    "external API gateway",
    "endpoint detection sensor",
    "container orchestration cluster",
    "email security gateway",
    "web application firewall",
    "database authentication path",
]

ISSUE_TYPES = [
    "unauthorized login attempt",
    "privilege escalation attempt",
    "MFA bypass alert",
    "suspicious lateral movement",
    "credential stuffing campaign",
    "data exfiltration pattern",
    "malicious code execution",
    "unusual privilege assignment",
    "suspicious firewall rule change",
    "sensitive file access",
    "zero-day exploit indicator",
    "DNS tunneling behavior",
    "scheduled task abuse",
    "cloud storage exposure",
    "privileged API token use",
    "identity federation failure",
    "unapproved software deployment",
    "security configuration drift",
    "endpoint compromise signal",
    "critical audit log deletion",
]

CATEGORY_MAP = {
    "unauthorized login attempt": "Security",
    "privilege escalation attempt": "Security",
    "MFA bypass alert": "Access Management",
    "suspicious lateral movement": "Security",
    "credential stuffing campaign": "Security",
    "data exfiltration pattern": "Security",
    "malicious code execution": "Application",
    "unusual privilege assignment": "Security",
    "suspicious firewall rule change": "Network",
    "sensitive file access": "Security",
    "zero-day exploit indicator": "Security",
    "DNS tunneling behavior": "Network",
    "scheduled task abuse": "Security",
    "cloud storage exposure": "Cloud",
    "privileged API token use": "Application",
    "identity federation failure": "Access Management",
    "unapproved software deployment": "Application",
    "security configuration drift": "Security",
    "endpoint compromise signal": "Infrastructure",
    "critical audit log deletion": "Security",
}

PRIORITY_MAP = {
    "Security": "P1",
    "Access Management": "P1",
    "Network": "P2",
    "Cloud": "P2",
    "Application": "P2",
    "Infrastructure": "P3",
}

SLA_MAP = {
    "P1": 4,
    "P2": 12,
    "P3": 24,
}

URGENCY_MAP = {
    "P1": "high",
    "P2": "medium",
    "P3": "low",
}

SEED_COUNT = 50
USER_NAME = "Karan Joshi"
USER_EMAIL = "requester@demo.local"
DEPARTMENT = "SecOps"


def generate_ticket_id(index: int) -> str:
    return f"KJ-SecOps-{index:03d}"


def build_issue(index: int) -> tuple[str, str, dict[str, object]]:
    issue = ISSUE_TYPES[index % len(ISSUE_TYPES)]
    context = CONTEXTS[index % len(CONTEXTS)]
    title = TITLE_TEMPLATES[index % len(TITLE_TEMPLATES)].format(issue.capitalize(), context)
    description = DESCRIPTION_TEMPLATES[index % len(DESCRIPTION_TEMPLATES)].format(
        issue,
        context,
        choice([
            "a credential compromise pattern",
            "an active brute-force vector",
            "an abnormal privilege escalation chain",
            "a failed MFA challenge sequence",
            "a misconfigured policy object",
            "a suspicious access token exchange",
            "a lateral movement signature",
            "a policy deviation event",
            "a suspicious network egress flow",
            "an unauthorized configuration change",
        ]),
    )
    category = CATEGORY_MAP.get(issue, "Security")
    priority = PRIORITY_MAP.get(category, "P2")
    metadata = {
        "category": category,
        "department": DEPARTMENT,
        "priority": priority,
        "sla_hours": SLA_MAP[priority],
        "hand": "3",
        "status": "OPEN",
        "seed": False,
        "requester_name": USER_NAME,
        "requester_email": USER_EMAIL,
        "ticket_type": "SecOps Incident",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    document = (
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Requester: {USER_NAME} <{USER_EMAIL}>\n"
        f"Department: {DEPARTMENT}\n"
        f"Category: {category}\n"
        f"Priority: {priority}\n"
        f"SLA Hours: {metadata['sla_hours']}"
    )
    return title, document, metadata


def get_session() -> object:
    init_db()
    return get_session_factory()()


def get_or_create_user(session):
    user = session.query(User).filter(User.email == USER_EMAIL).one_or_none()
    if user:
        return user
    user = User(email=USER_EMAIL, role="requester", department=DEPARTMENT)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def build_sql_ticket(user, index: int) -> tuple[Ticket, ClassificationArtifact, ResolutionArtifact]:
    title, description, metadata = build_issue(index)
    priority = metadata["priority"]
    ticket_id = generate_ticket_id(index + 1)
    created_at = datetime.utcnow() - timedelta(hours=index * 2)
    updated_at = created_at + timedelta(hours=1)
    ticket = Ticket(
        ticket_id=ticket_id,
        user_id=user.user_id,
        title=title,
        description_raw=description,
        description_sanitized=description,
        urgency=URGENCY_MAP[priority],
        status="OPEN",
        hand="3",
        confidence=0.78,
        department_queue=DEPARTMENT,
        priority=priority,
        sla_hours=SLA_MAP[priority],
        escalation_required=priority == "P1",
        created_at=created_at,
        updated_at=updated_at,
    )
    steps = [
        f"Review the {metadata['category']} alert and identify affected system.",
        "Contain the incident and isolate impacted resources.",
        "Apply SecOps remediation playbook steps and validate changes.",
        "Document the resolution and close the ticket once verified.",
    ]
    citations = [
        "KB-SEC-001",
        "KB-SEC-002",
    ]
    classification = ClassificationArtifact(
        ticket_id=ticket_id,
        use_case_category=metadata["category"],
        subcategory="SecOps Incident",
        confidence_hint="high",
        source="generated",
    )
    resolution = ResolutionArtifact(
        ticket_id=ticket_id,
        steps_json=json.dumps(steps),
        citations_json=json.dumps(citations),
        low_grounding=False,
        similarity_score=0.78,
    )
    return ticket, classification, resolution


def seed_sql_tickets() -> int:
    session = get_session()
    user = get_or_create_user(session)
    existing_ids = set(session.query(Ticket.ticket_id).scalars().all())
    inserted = 0

    for index in range(SEED_COUNT):
        ticket_id = generate_ticket_id(index + 1)
        if ticket_id in existing_ids:
            continue
        ticket, classification, resolution = build_sql_ticket(user, index)
        session.add(ticket)
        session.add(classification)
        session.add(resolution)
        inserted += 1

    if inserted:
        session.commit()
    session.close()
    return inserted


def seed_chroma_tickets() -> int:
    store = ChromaTicketStore()
    if not store.available:
        raise RuntimeError("ChromaDB store is unavailable; check chroma persistence setup.")

    inserted = 0
    for index in range(SEED_COUNT):
        ticket_id = generate_ticket_id(index + 1)
        title, document, metadata = build_issue(index)
        store.upsert(ticket_id, document, metadata)
        inserted += 1

    return inserted


def main() -> None:
    chroma_inserted = seed_chroma_tickets()
    sql_inserted = seed_sql_tickets()
    print(f"Inserted {chroma_inserted} SecOps tickets for {USER_NAME} into ChromaDB.")
    print(f"Inserted {sql_inserted} SecOps tickets for {USER_NAME} into SQLite.")


if __name__ == "__main__":
    main()
