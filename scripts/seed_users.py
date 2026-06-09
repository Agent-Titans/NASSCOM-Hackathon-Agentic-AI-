#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.models import Ticket, User  # noqa: E402
from src.db.session import get_session_factory, init_db  # noqa: E402

# (email, role, department) — emails stored lowercase; default password 1234 (see demo_auth)
SEED_USERS = [
    # Employee portal
    ("pallavi@user", "requester", None),
    ("gajanan@user", "requester", None),
    ("imran@user", "requester", None),
    ("naveen@user", "requester", None),
    ("santhosh@user", "requester", None),
    # Agent workspace
    ("sree@employee", "assignee", "Hardware"),
    ("subbu@employee", "assignee", "Software"),
    ("sruthi@employee", "assignee", "Software"),
    ("shashi@employee", "assignee", "Network"),
    ("narsimha@employee", "assignee", "SecOps"),
    ("chandana@employee", "assignee", "SecOps"),
    ("satya@employee", "assignee", "Access Management"),
    ("sagar@employee", "assignee", "DBA"),
    ("admin@employee", "admin", None),
]


def main() -> None:
    init_db()
    Session = get_session_factory()
    canonical_assignees = {email for email, role, _ in SEED_USERS if role == "assignee"}
    with Session() as session:
        for email, role, department in SEED_USERS:
            existing = session.query(User).filter(User.email == email).first()
            if existing:
                existing.role = role
                existing.department = department
                continue
            session.add(User(email=email, role=role, department=department))

        # Retire pre-IntelliQ demo assignees (e.g. software@demo.local) left in SQLite.
        stale_assignees = (
            session.query(User)
            .filter(User.role == "assignee", ~User.email.in_(canonical_assignees))
            .all()
        )
        for user in stale_assignees:
            user.role = "requester"
            user.department = None
        migrated_users = (
            session.query(User).filter(User.department == "Identity").update(
                {"department": "Access Management"}, synchronize_session=False
            )
        )
        migrated_tickets = (
            session.query(Ticket).filter(Ticket.department_queue == "Identity").update(
                {"department_queue": "Access Management"}, synchronize_session=False
            )
        )
        session.commit()
    print("Seeded users:", ", ".join(u[0] for u in SEED_USERS))
    if migrated_users or migrated_tickets:
        print(
            f"Migrated legacy Identity → Access Management: "
            f"{migrated_users} user(s), {migrated_tickets} ticket(s)"
        )


if __name__ == "__main__":
    main()
