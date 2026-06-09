#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.models import User  # noqa: E402
from src.db.session import get_session_factory, init_db  # noqa: E402

SEED_USERS = [
    ("requester@demo.local", "requester", None),
    ("emily.reed@demo.local", "requester", None),
    ("james.wu@demo.local", "requester", None),
    ("sarah.kim@demo.local", "requester", None),
    ("michael.brown@demo.local", "requester", None),
    ("hardware@demo.local", "assignee", "Hardware"),
    ("software@demo.local", "assignee", "Software"),
    ("secops@demo.local", "assignee", "SecOps"),
    ("network@demo.local", "assignee", "Network"),
    ("identity@demo.local", "assignee", "Identity"),
    ("dba@demo.local", "assignee", "DBA"),
    ("storage@demo.local", "assignee", "Storage"),
    ("admin@demo.local", "admin", None),
]


def main() -> None:
    init_db()
    Session = get_session_factory()
    with Session() as session:
        for email, role, department in SEED_USERS:
            existing = session.query(User).filter(User.email == email).first()
            if existing:
                existing.role = role
                existing.department = department
                continue
            session.add(User(email=email, role=role, department=department))
        session.commit()
    print("Seeded users:", ", ".join(u[0] for u in SEED_USERS))


if __name__ == "__main__":
    main()
