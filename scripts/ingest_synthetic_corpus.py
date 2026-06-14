#!/usr/bin/env python3
"""
Ingest synthetic 1k corpus into SQLite (RESOLVED) + ChromaDB for RAG retrieval.

Prerequisites: scripts/seed_users.py, data/synthetic/tickets_1000.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.departments import canonical_department, department_queue_aliases  # noqa: E402
from src.config.settings import get_settings  # noqa: E402
from src.data.synthetic_corpus import (  # noqa: E402
    synthetic_row_metadata,
    synthetic_search_document,
)
from src.data.synthetic_corpus_generator import write_corpus  # noqa: E402
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket, User  # noqa: E402
from src.db.session import get_session_factory, init_db  # noqa: E402
from src.services.ticket_retrieval import TicketRetrievalService, chroma_corpus_entries  # noqa: E402

_REQUESTERS = (
    "pallavi@user",
    "gajanan@user",
    "imran@user",
    "naveen@user",
    "santhosh@user",
    "requester@demo.local",
)


def _load_tickets(path: Path) -> list[dict]:
    if not path.exists():
        write_corpus(path)
        print(f"Generated missing corpus at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("tickets", []))


def _assignee_for_department(session, department: str) -> str | None:
    canon = canonical_department(department)
    queues = list(department_queue_aliases(canon))
    agents = (
        session.query(User)
        .filter(User.role == "assignee", User.department.in_(queues))
        .order_by(User.email)
        .all()
    )
    if not agents:
        return None
    return agents[0].user_id


def seed_sqlite_resolved(session, tickets: list[dict], *, batch: int = 200) -> int:
    users = {u.email: u for u in session.query(User).all()}
    requesters = [users[e] for e in _REQUESTERS if e in users]
    if not requesters:
        raise RuntimeError("No requesters found — run scripts/seed_users.py first")

    # Remove prior synthetic resolved tickets only
    syn_ids = [t["id"] for t in tickets]
    if syn_ids:
        session.query(ResolutionArtifact).filter(
            ResolutionArtifact.ticket_id.in_(syn_ids)
        ).delete(synchronize_session=False)
        session.query(ClassificationArtifact).filter(
            ClassificationArtifact.ticket_id.in_(syn_ids)
        ).delete(synchronize_session=False)
        session.query(Ticket).filter(Ticket.ticket_id.in_(syn_ids)).delete(
            synchronize_session=False
        )
        session.commit()

    count = 0
    for idx, row in enumerate(tickets):
        ticket_id = row["id"]
        hand = str(row["hand"])
        department = canonical_department(str(row.get("department") or ""))
        requester = requesters[idx % len(requesters)]
        assignee_id = None if hand == "1" else _assignee_for_department(session, department)

        ticket = Ticket(
            ticket_id=ticket_id,
            user_id=requester.user_id,
            assignee_id=assignee_id,
            title=row["title"],
            description_raw=row["description"],
            description_sanitized=row["description"],
            urgency=row.get("urgency", "medium"),
            status="RESOLVED",
            hand=hand,
            department_queue=department,
            priority=row.get("priority", "P2"),
            sla_hours=int(row.get("sla_hours", 24)),
            escalation_required=hand == "3" or row["category"] == "Security",
            confidence=0.88 if hand == "1" else 0.72 if hand == "2" else 0.42,
        )
        session.add(ticket)

        clf = ClassificationArtifact(
            ticket_id=ticket_id,
            use_case_category=row["category"],
            subcategory=f"synthetic_h{hand}",
            confidence_hint="high" if hand == "1" else "medium" if hand == "2" else "low",
            source="rag",
        )
        session.add(clf)

        res = ResolutionArtifact(
            ticket_id=ticket_id,
            steps_json=json.dumps(row["resolution_steps"]),
            citations_json=json.dumps(row.get("citations", [])),
            low_grounding=False,
            similarity_score=0.9 if hand == "1" else 0.72 if hand == "2" else 0.55,
        )
        session.add(res)
        count += 1

        if count % batch == 0:
            session.commit()

    session.commit()
    return count


def build_chroma_entries(tickets: list[dict]) -> list[tuple[str, str, dict]]:
    entries: list[tuple[str, str, dict]] = []
    for row in tickets:
        doc = synthetic_search_document(
            (
                row["id"],
                row["title"],
                row["description"],
                row["category"],
                str(row["hand"]),
                row["resolution_steps"],
                row.get("citations", []),
            )
        )
        meta = synthetic_row_metadata(row)
        meta["seed"] = False
        entries.append((row["id"], doc, meta))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest synthetic corpus into SQLite + Chroma.")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="Path to tickets JSON (default: settings.synthetic_corpus_path)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run retrieval smoke queries after ingest (slower)",
    )
    parser.add_argument(
        "--skip-chroma",
        action="store_true",
        help="Skip Gemini Chroma index (SQLite keyword fallback only)",
    )
    args = parser.parse_args()

    settings = get_settings()
    corpus_path = args.corpus or settings.synthetic_corpus_path
    print(f"Loading corpus from {corpus_path}…", flush=True)
    tickets = _load_tickets(corpus_path)
    if not tickets:
        print("No tickets to ingest.")
        return 1

    print(f"Seeding {len(tickets)} RESOLVED tickets into SQLite…", flush=True)
    init_db()
    Session = get_session_factory()
    with Session() as session:
        sqlite_count = seed_sqlite_resolved(session, tickets)
        print(f"SQLite: upserted {sqlite_count} RESOLVED synthetic tickets", flush=True)

    svc = TicketRetrievalService()
    if args.skip_chroma:
        print("Skipping Chroma — SQLite keyword fallback only.", flush=True)
        chroma_count = 0
        mode = "skipped"
    else:
        backend = settings.rag_embedding_backend
        print(
            f"Indexing ChromaDB ({backend} embeddings, "
            f"KB + {len(tickets)} synthetic tickets)…",
            flush=True,
        )
        chroma_payload = build_chroma_entries(tickets)
        chroma_count = svc.index_synthetic_chroma(chroma_payload)
        mode = getattr(svc.chroma, "_embedding_mode", "none")
    kb = len(chroma_corpus_entries())
    print(
        f"ChromaDB: {chroma_count} documents indexed "
        f"(~{kb} KB + {len(tickets)} synthetic, mode={mode})",
        flush=True,
    )

    if args.smoke:
        print("Smoke retrieval:", flush=True)
        with Session() as session:
            for label, text in (
                ("password", "I forgot my password and cannot login"),
                ("printer", "Printer paper jammed in office"),
                ("security", "AWS secret key exposed on GitHub"),
            ):
                match = svc.find_similar(session, text)
                if match:
                    print(
                        f"  {label}: {match.ticket_id} → {match.department_queue} "
                        f"({match.classification.use_case_category}, h{match.source_hand}, "
                        f"score={match.similarity_score:.2f}",
                        flush=True,
                    )
                else:
                    print(f"  {label}: no match", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
