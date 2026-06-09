"""Find similar resolved tickets — ChromaDB BM25 + DB keyword overlap."""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from src.data.enterprise_rag_corpus import (
    ENTERPRISE_RAG_CORPUS,
    enterprise_search_document,
)
from src.data.rag_demo_corpus import (
    RAG_DEMO_CORPUS,
    corpus_search_document,
    demo_ticket_routing,
    department_for_category,
)
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket
from src.models.schemas import ClassificationResult, ResolutionResult, SimilarTicketMatch
from src.config.rag_policy import confidence_hint_from_similarity, is_low_grounding_similarity
from src.stores.chroma_store import ChromaTicketStore

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")
_MIN_SIMILARITY = 0.28

# Seed knowledge when DB is sparse (maps to demo playbooks)
_KB_SEEDS: list[tuple[str, str, str, list[str], list[str]]] = [
    (
        "kb-access-001",
        "Forgot password cannot login MFA locked out access account Windows login active directory "
        "corporate password reset locked out",
        "Access Management",
        [
            "Open the company password portal.",
            "Choose Forgot password and verify your identity.",
            "Follow the email link to set a new password (12+ characters).",
            "Sign in again; if MFA fails, contact Identity from this ticket.",
        ],
        ["KB-ACCESS-001", "TICKET-1042"],
    ),
    (
        "kb-net-007",
        "VPN wifi network connection dns internet cannot connect",
        "Network",
        [
            "Restart VPN client and re-authenticate.",
            "Forget and rejoin Wi-Fi using corporate credentials.",
            "Run built-in network diagnostics and note error codes.",
        ],
        ["KB-NET-007"],
    ),
    (
        "kb-hw-014",
        "Printer print toner paper jam hardware",
        "Infrastructure",
        [
            "Confirm the printer is online and has paper/toner.",
            "Remove jammed paper following the panel guide.",
            "Reinstall the driver from the internal software catalog.",
        ],
        ["KB-HW-014"],
    ),
    (
        "kb-app-020",
        "Software application crash bug install update excel macro",
        "Application",
        [
            "Confirm the application version and recent updates.",
            "Clear cache and restart the application.",
            "Reinstall from the internal software catalog if crashes persist.",
        ],
        ["KB-APP-020"],
    ),
    (
        "kb-db-011",
        "Database query slow replication sql deadlock report",
        "Database",
        [
            "Identify long-running queries on the affected database.",
            "Check replication lag and blocking sessions.",
            "Apply standard DBA runbook for query tuning or failover.",
        ],
        ["KB-DB-011"],
    ),
    (
        "kb-storage-009",
        "Storage backup disk share quota file nas archive",
        "Storage",
        [
            "Verify storage capacity and quota on the affected share.",
            "Clear stale files or expand quota per policy.",
            "Retry backup job after confirming NAS connectivity.",
        ],
        ["KB-STORAGE-009"],
    ),
]

_DEPT_MAP = {
    "Infrastructure": "Hardware",
    "Application": "Software",
    "Security": "SecOps",
    "Database": "DBA",
    "Storage": "Storage",
    "Network": "Network",
    "Access Management": "Identity",
}


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _keyword_overlap(query: str, candidate: str) -> float:
    q, c = _tokenize(query), _tokenize(candidate)
    if not q or not c:
        return 0.0
    return len(q & c) / len(q | c)


# (id, search_doc, category, steps, citations, hand)
_CorpusRow = tuple[str, str, str, list[str], list[str], str]

_DEMO_CORPUS: list[_CorpusRow] = [
    (
        entry[0],
        corpus_search_document(entry),
        entry[3],
        entry[5],
        entry[6],
        entry[4],
    )
    for entry in RAG_DEMO_CORPUS
]

_ENTERPRISE_CORPUS: list[_CorpusRow] = [
    (
        entry[0],
        enterprise_search_document(entry),
        entry[3],
        entry[5],
        entry[6],
        entry[4],
    )
    for entry in ENTERPRISE_RAG_CORPUS
]

_KB_CORPUS: list[_CorpusRow] = [
    (seed_id, doc, category, steps, cites, "1")
    for seed_id, doc, category, steps, cites in _KB_SEEDS
]


def _all_corpus_rows() -> list[_CorpusRow]:
    return _KB_CORPUS + _DEMO_CORPUS + _ENTERPRISE_CORPUS


def _is_corpus_id(doc_id: str) -> bool:
    return (
        doc_id.startswith("kb-")
        or doc_id.startswith("rag-")
        or doc_id.startswith("ent-")
    )


def chroma_corpus_entries() -> list[tuple[str, str, dict]]:
    """Build Chroma upsert payload for KB seeds + demo corpus."""
    rows: list[tuple[str, str, dict]] = []
    for doc_id, doc, category, _steps, _cites, hand in _all_corpus_rows():
        meta: dict[str, object] = {
            "category": category,
            "department": department_for_category(category),
            "hand": hand,
            "seed": True,
        }
        if doc_id.startswith("rag-") or doc_id.startswith("ent-"):
            route = demo_ticket_routing(doc_id, category, hand)
            meta["priority"] = route["priority"]
            meta["sla_hours"] = route["sla_hours"]
            meta["department"] = route["department_queue"]
            meta["complexity_tier"] = "H1" if hand == "1" else "H2" if hand == "2" else "H3"
        else:
            meta["priority"] = "P2"
            meta["sla_hours"] = 24
        rows.append((doc_id, doc, meta))
    return rows


class TicketRetrievalService:
    def __init__(self, chroma: ChromaTicketStore | None = None) -> None:
        self.chroma = chroma or ChromaTicketStore()

    def index_corpus(self) -> int:
        """Load KB seeds + 45 demo tickets into ChromaDB. Returns document count."""
        if not self.chroma.available:
            return 0
        return self.chroma.reindex_all(chroma_corpus_entries())

    def ensure_index(self, session: Session) -> None:
        """Index resolved tickets + corpus into Chroma when available."""
        if self.chroma.available and self.chroma.count == 0:
            for doc_id, doc, meta in chroma_corpus_entries():
                self.chroma.upsert(doc_id, doc, meta)

        tickets = (
            session.query(Ticket)
            .filter(Ticket.status == "RESOLVED")
            .order_by(Ticket.updated_at.desc())
            .limit(200)
            .all()
        )
        for t in tickets:
            clf = (
                session.query(ClassificationArtifact)
                .filter_by(ticket_id=t.ticket_id)
                .first()
            )
            res = (
                session.query(ResolutionArtifact)
                .filter_by(ticket_id=t.ticket_id)
                .first()
            )
            if not res or not self.chroma.available:
                continue
            steps = json.loads(res.steps_json or "[]")
            if not steps:
                continue
            doc = f"{t.title}\n{t.description_sanitized or t.description_raw}"
            self.chroma.upsert(
                t.ticket_id,
                doc,
                {
                    "category": clf.use_case_category if clf else "",
                    "department": t.department_queue or "",
                    "priority": t.priority or "P2",
                    "sla_hours": t.sla_hours or 24,
                    "hand": t.hand or "",
                    "seed": False,
                },
            )

    def find_similar(
        self,
        session: Session,
        text: str,
        *,
        exclude_ticket_id: Optional[str] = None,
    ) -> Optional[SimilarTicketMatch]:
        self.ensure_index(session)
        if not text.strip():
            return None

        candidates: dict[str, float] = {}

        if self.chroma.available:
            for tid, sim in self.chroma.query(text, top_k=8):
                if exclude_ticket_id and tid == exclude_ticket_id:
                    continue
                if _is_corpus_id(tid):
                    candidates[tid] = max(candidates.get(tid, 0.0), sim)
                else:
                    ticket = session.get(Ticket, tid)
                    if ticket and ticket.status == "RESOLVED":
                        candidates[tid] = max(candidates.get(tid, 0.0), sim)

        # Corpus — always scored via keyword overlap (works without Chroma)
        for doc_id, doc, _cat, _steps, _cites, _hand in _all_corpus_rows():
            overlap = _keyword_overlap(text, doc)
            if overlap > 0:
                candidates[doc_id] = max(candidates.get(doc_id, 0.0), overlap)

        # DB keyword overlap on resolved tickets (keyword match complement)
        resolved = (
            session.query(Ticket)
            .filter(Ticket.status == "RESOLVED")
            .order_by(Ticket.updated_at.desc())
            .limit(100)
            .all()
        )
        for t in resolved:
            if exclude_ticket_id and t.ticket_id == exclude_ticket_id:
                continue
            doc = f"{t.title} {t.description_sanitized or t.description_raw}"
            overlap = _keyword_overlap(text, doc)
            if overlap > 0:
                candidates[t.ticket_id] = max(candidates.get(t.ticket_id, 0.0), overlap)

        if not candidates:
            return None

        best_id = max(candidates, key=candidates.get)
        best_score = candidates[best_id]
        if best_score < _MIN_SIMILARITY:
            return None

        if _is_corpus_id(best_id):
            return self._match_from_corpus(best_id, best_score)

        return self._match_from_ticket(session, best_id, best_score, source="chroma")

    def _match_from_corpus(self, doc_id: str, score: float) -> Optional[SimilarTicketMatch]:
        for sid, doc, category, steps, cites, hand in _all_corpus_rows():
            if sid != doc_id:
                continue
            if sid.startswith("rag-"):
                dept = str(demo_ticket_routing(sid, category, hand)["department_queue"])
            else:
                dept = _DEPT_MAP.get(category, "Software")
            sub = "kb_seed" if sid.startswith("kb-") else f"rag_demo_h{hand}"
            hint = confidence_hint_from_similarity(score)
            low_grounding = is_low_grounding_similarity(score)
            return SimilarTicketMatch(
                ticket_id=doc_id,
                title=doc[:80],
                similarity_score=score,
                classification=ClassificationResult(
                    use_case_category=category,
                    subcategory=sub,
                    confidence_hint=hint,
                    source="rag",
                ),
                resolution=ResolutionResult(
                    steps=steps,
                    citations=cites,
                    low_grounding=low_grounding,
                    similarity_score=score,
                    matched_ticket_id=doc_id,
                    matched_source_hand=hand,
                ),
                department_queue=dept,
                source="chroma",
                source_hand=hand,
            )
        return None

    def _match_from_ticket(
        self,
        session: Session,
        ticket_id: str,
        score: float,
        source: str,
    ) -> Optional[SimilarTicketMatch]:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return None
        clf = (
            session.query(ClassificationArtifact)
            .filter_by(ticket_id=ticket_id)
            .first()
        )
        res = (
            session.query(ResolutionArtifact)
            .filter_by(ticket_id=ticket_id)
            .first()
        )
        if not res:
            return None
        steps = json.loads(res.steps_json or "[]")
        if not steps:
            return None
        cites = json.loads(res.citations_json or "[]")
        category = clf.use_case_category if clf else "Application"
        hint = confidence_hint_from_similarity(score)
        low_grounding = is_low_grounding_similarity(score)
        ticket_hand = ticket.hand if ticket.hand in ("1", "2", "3") else None
        return SimilarTicketMatch(
            ticket_id=ticket_id,
            title=ticket.title,
            similarity_score=score,
            classification=ClassificationResult(
                use_case_category=category,
                subcategory=clf.subcategory if clf else None,
                confidence_hint=hint,
                source="rag",
            ),
            resolution=ResolutionResult(
                steps=steps,
                citations=cites,
                low_grounding=low_grounding,
                similarity_score=score,
                matched_ticket_id=ticket_id,
                matched_source_hand=ticket_hand,
            ),
            department_queue=ticket.department_queue or _DEPT_MAP.get(category, "Software"),
            source=source,
            source_hand=ticket_hand,
        )
