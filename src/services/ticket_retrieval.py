"""Find similar resolved tickets — Chroma BM25 + stemmed keywords + Gemini embeddings."""
from __future__ import annotations

import json
import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from src.data.enterprise_rag_corpus import (
    ENTERPRISE_RAG_CORPUS,
    enterprise_search_document,
)
from src.data.kb_seed_corpus import KB_SEED_CORPUS
from src.data.rag_demo_corpus import (
    RAG_DEMO_CORPUS,
    corpus_search_document,
    demo_ticket_routing,
    department_for_category,
)
from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket
from src.models.schemas import (
    ClassificationResult,
    ResolutionResult,
    RetrievalReference,
    SimilarTicketMatch,
)
from src.config.rag_policy import confidence_hint_from_similarity, is_low_grounding_similarity
from src.config.settings import get_settings
from src.services.process_cache import (
    get_retrieval_candidates,
    retrieval_cache_key,
    set_retrieval_candidates,
)
from src.services.semantic_similarity import (
    corpus_fingerprint,
    corpus_semantic_scores,
    stemmed_jaccard,
    stemmed_jaccard_sets,
    stem_tokenize,
    user_ticket_semantic_scores,
    hydrate_corpus_embeddings_from_disk,
    warm_corpus_embedding_cache,
)
from src.stores.embedding_cache_store import get_embedding_cache_store
from src.stores.chroma_store import ChromaTicketStore

logger = logging.getLogger(__name__)

_MIN_SIMILARITY = 0.28
_corpus_cache_hydrated = False
_indexed_resolved_ids: set[str] = set()
_ensure_index_done = False

# Seed knowledge when DB is sparse (maps to demo playbooks)
_DEPT_MAP = {
    "Infrastructure": "Hardware",
    "Application": "Software",
    "Security": "SecOps",
    "Database": "DBA",
    "Storage": "DBA",
    "Network": "Network",
    "Access Management": "Access Management",
}


def _keyword_overlap(query: str, candidate: str) -> float:
    """Stemmed Jaccard overlap — jam/jammed/printing collapse to shared roots."""
    return stemmed_jaccard(query, candidate)


# Pre-stemmed corpus docs — built once per process.
_CORPUS_STEMS: dict[str, set[str]] = {}


def _corpus_stems(doc_id: str, doc: str) -> set[str]:
    stems = _CORPUS_STEMS.get(doc_id)
    if stems is None:
        stems = stem_tokenize(doc)
        _CORPUS_STEMS[doc_id] = stems
    return stems


def _corpus_keyword_overlap(query: str, doc_id: str, doc: str) -> float:
    return stemmed_jaccard_sets(stem_tokenize(query), _corpus_stems(doc_id, doc))


def _ensure_corpus_stems() -> None:
    if _CORPUS_STEMS:
        return
    for doc_id, doc, *_rest in _all_corpus_rows():
        _CORPUS_STEMS[doc_id] = stem_tokenize(doc)


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
    for seed_id, doc, category, steps, cites in KB_SEED_CORPUS
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
        global _corpus_cache_hydrated, _ensure_index_done, _indexed_resolved_ids

        if self.chroma.available and self.chroma.count == 0:
            for doc_id, doc, meta in chroma_corpus_entries():
                self.chroma.upsert(doc_id, doc, meta)

        rows = _all_corpus_rows()
        _ensure_corpus_stems()
        if not _corpus_cache_hydrated:
            loaded = hydrate_corpus_embeddings_from_disk(rows)
            _corpus_cache_hydrated = True
            if loaded:
                logger.info("Hydrated %d corpus embedding vectors from disk", loaded)

        if _ensure_index_done and not self.chroma.available:
            return

        tickets = (
            session.query(Ticket)
            .filter(Ticket.status == "RESOLVED")
            .order_by(Ticket.updated_at.desc())
            .limit(200)
            .all()
        )
        pending = [t for t in tickets if t.ticket_id not in _indexed_resolved_ids]
        if pending and self.chroma.available:
            ticket_ids = [t.ticket_id for t in pending]
            artifacts = {
                row.ticket_id: row
                for row in session.query(ClassificationArtifact).filter(
                    ClassificationArtifact.ticket_id.in_(ticket_ids)
                )
            }
            resolutions = {
                row.ticket_id: row
                for row in session.query(ResolutionArtifact).filter(
                    ResolutionArtifact.ticket_id.in_(ticket_ids)
                )
            }
            for t in pending:
                res = resolutions.get(t.ticket_id)
                if not res:
                    continue
                steps = json.loads(res.steps_json or "[]")
                if not steps:
                    continue
                clf = artifacts.get(t.ticket_id)
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
                _indexed_resolved_ids.add(t.ticket_id)

        _ensure_index_done = True

    def _collect_candidates(
        self,
        session: Session,
        text: str,
        *,
        exclude_ticket_id: Optional[str] = None,
    ) -> dict[str, float]:
        """Score RAG corpus + resolved user tickets (BM25/keywords + targeted embeddings)."""
        if not text.strip():
            return {}

        cache_key = retrieval_cache_key(text, exclude_ticket_id)
        cached = get_retrieval_candidates(cache_key)
        if cached is not None:
            return dict(cached)

        self.ensure_index(session)
        candidates: dict[str, float] = {}

        settings = get_settings()
        chroma_corpus_ids: list[str] = []

        if self.chroma.available:
            for tid, sim in self.chroma.query(text, top_k=settings.rag_top_k):
                if exclude_ticket_id and tid == exclude_ticket_id:
                    continue
                if _is_corpus_id(tid):
                    candidates[tid] = max(candidates.get(tid, 0.0), sim)
                    chroma_corpus_ids.append(tid)
                else:
                    ticket = session.get(Ticket, tid)
                    if ticket and ticket.status == "RESOLVED":
                        candidates[tid] = max(candidates.get(tid, 0.0), sim)

        corpus_rows = _all_corpus_rows()
        keyword_corpus_ids: set[str] = set()

        for doc_id, doc, _cat, _steps, _cites, _hand in corpus_rows:
            overlap = _corpus_keyword_overlap(text, doc_id, doc)
            if overlap > 0:
                candidates[doc_id] = max(candidates.get(doc_id, 0.0), overlap)
                keyword_corpus_ids.add(doc_id)

        semantic_ids: set[str] = set(chroma_corpus_ids[: settings.retrieval_semantic_candidate_cap])
        semantic_ids |= keyword_corpus_ids
        if len(semantic_ids) > settings.retrieval_semantic_candidate_cap:
            ranked = sorted(
                semantic_ids,
                key=lambda doc_id: candidates.get(doc_id, 0.0),
                reverse=True,
            )
            semantic_ids = set(ranked[: settings.retrieval_semantic_candidate_cap])

        pre_semantic_best = max(candidates.values()) if candidates else 0.0
        skip_semantic = (
            settings.retrieval_skip_semantic_when_strong
            and pre_semantic_best >= settings.rag_sim_high
        )
        if semantic_ids and not skip_semantic:
            for doc_id, sim in corpus_semantic_scores(
                text, corpus_rows, doc_ids=semantic_ids
            ).items():
                candidates[doc_id] = max(candidates.get(doc_id, 0.0), sim)

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
            if _is_corpus_id(t.ticket_id):
                continue
            doc = f"{t.title} {t.description_sanitized or t.description_raw}"
            overlap = _keyword_overlap(text, doc)
            if overlap > 0:
                candidates[t.ticket_id] = max(candidates.get(t.ticket_id, 0.0), overlap)

        user_ids = {tid for tid in candidates if not _is_corpus_id(tid)}
        if user_ids:
            user_docs: dict[str, str] = {}
            for t in resolved:
                if t.ticket_id in user_ids:
                    user_docs[t.ticket_id] = (
                        f"{t.title}\n{t.description_sanitized or t.description_raw}"
                    )
            for tid in user_ids:
                if tid in user_docs:
                    continue
                ticket = session.get(Ticket, tid)
                if ticket:
                    user_docs[tid] = (
                        f"{ticket.title}\n"
                        f"{ticket.description_sanitized or ticket.description_raw}"
                    )
            for tid, sim in user_ticket_semantic_scores(text, user_docs).items():
                candidates[tid] = max(candidates.get(tid, 0.0), sim)

        set_retrieval_candidates(cache_key, candidates)
        return candidates

    @staticmethod
    def _corpus_category(doc_id: str) -> str:
        for sid, _doc, category, *_rest in _all_corpus_rows():
            if sid == doc_id:
                return category
        return "Application"

    @staticmethod
    def _references_from_candidates(
        session: Session,
        candidates: dict[str, float],
        *,
        query_text: str = "",
    ) -> list[RetrievalReference]:
        """Best relevant RAG corpus hit + best relevant user resolved hit."""
        from src.services.rag_relevance import is_reference_relevant

        if not candidates:
            return []

        corpus_pool = {
            tid: score
            for tid, score in candidates.items()
            if _is_corpus_id(tid) and score >= _MIN_SIMILARITY
        }
        user_pool: dict[str, float] = {}
        for tid, score in candidates.items():
            if _is_corpus_id(tid) or score < _MIN_SIMILARITY:
                continue
            ticket = session.get(Ticket, tid)
            if ticket and ticket.status == "RESOLVED":
                user_pool[tid] = score

        refs: list[RetrievalReference] = []

        def _append_if_relevant(ref: RetrievalReference, category: str) -> bool:
            if not query_text.strip():
                refs.append(ref)
                return True
            if is_reference_relevant(
                query_text,
                ticket_id=ref.ticket_id,
                title=ref.title,
                score=ref.score,
                source=ref.source,
                category=category,
            ):
                refs.append(ref)
                return True
            return False

        for best_id, score in sorted(corpus_pool.items(), key=lambda item: -item[1]):
            ref = TicketRetrievalService._to_retrieval_reference(
                session, best_id, score, "rag"
            )
            if _append_if_relevant(ref, TicketRetrievalService._corpus_category(best_id)):
                break

        for best_id, score in sorted(user_pool.items(), key=lambda item: -item[1]):
            ticket = session.get(Ticket, best_id)
            clf = (
                session.query(ClassificationArtifact)
                .filter_by(ticket_id=best_id)
                .first()
            )
            category = clf.use_case_category if clf else "Application"
            ref = TicketRetrievalService._to_retrieval_reference(
                session, best_id, score, "user"
            )
            if _append_if_relevant(ref, category):
                break

        return refs

    def find_best_references(
        self,
        session: Session,
        text: str,
        *,
        exclude_ticket_id: Optional[str] = None,
    ) -> list[RetrievalReference]:
        candidates = self._collect_candidates(
            session, text, exclude_ticket_id=exclude_ticket_id
        )
        return self._references_from_candidates(session, candidates, query_text=text)

    def find_similar_and_references(
        self,
        session: Session,
        text: str,
        *,
        exclude_ticket_id: Optional[str] = None,
    ) -> Tuple[Optional[SimilarTicketMatch], list[RetrievalReference]]:
        """Single retrieval pass — similar match + reference links."""
        candidates = self._collect_candidates(
            session, text, exclude_ticket_id=exclude_ticket_id
        )
        refs = self._references_from_candidates(session, candidates, query_text=text)
        if not candidates:
            return None, refs

        best_id = max(candidates, key=candidates.get)
        best_score = candidates[best_id]
        if best_score < _MIN_SIMILARITY:
            return None, refs

        if _is_corpus_id(best_id):
            match = self._match_from_corpus(best_id, best_score)
        else:
            match = self._match_from_ticket(session, best_id, best_score, source="chroma")
        return match, refs

    @staticmethod
    def _to_retrieval_reference(
        session: Session,
        ticket_id: str,
        score: float,
        source: str,
    ) -> RetrievalReference:
        canon_id = ticket_id.lower() if _is_corpus_id(ticket_id) else ticket_id
        ticket = session.get(Ticket, canon_id)
        title = (ticket.title if ticket else "")[:80]
        if _is_corpus_id(canon_id):
            label = canon_id.upper()
        else:
            label = f"INC-{canon_id[:8].upper()}"
        return RetrievalReference(
            ticket_id=canon_id,
            label=label,
            score=round(score, 3),
            source=source,
            title=title,
        )

    def find_similar(
        self,
        session: Session,
        text: str,
        *,
        exclude_ticket_id: Optional[str] = None,
    ) -> Optional[SimilarTicketMatch]:
        match, _refs = self.find_similar_and_references(
            session, text, exclude_ticket_id=exclude_ticket_id
        )
        return match

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
                    matched_source_hand=str(hand) if hand else None,
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


def mark_resolved_ticket_for_index(ticket_id: str) -> None:
    """Re-index this ticket on next retrieval pass after resolve."""
    global _indexed_resolved_ids
    _indexed_resolved_ids.discard(ticket_id)
