#!/usr/bin/env python3
"""Lightweight SQLite migrations for demo DB."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text  # noqa: E402

from src.db.models import Base, TicketComment  # noqa: E402
from src.db.session import get_engine, init_db  # noqa: E402


def _column_names(engine, table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def main() -> None:
    init_db()
    engine = get_engine()
    with engine.begin() as conn:
        if "tickets" in inspect(engine).get_table_names():
            cols = _column_names(engine, "tickets")
            if "assignee_id" not in cols:
                conn.execute(
                    text("ALTER TABLE tickets ADD COLUMN assignee_id VARCHAR(36)")
                )
                print("Added tickets.assignee_id")
            else:
                print("tickets.assignee_id already present")
        Base.metadata.create_all(bind=engine, tables=[TicketComment.__table__])
        print("Ensured ticket_comments table")
    print("Schema migration complete.")


if __name__ == "__main__":
    main()
