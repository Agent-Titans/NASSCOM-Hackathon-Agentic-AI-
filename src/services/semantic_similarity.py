"""Stemmed tokens + Gemini embedding cosine similarity for RAG retrieval."""
from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Set, Tuple

import snowballstemmer

from src.clients.gemini_client import GeminiClient
from src.config.settings import get_settings
from src.stores.embedding_cache_store import get_embedding_cache_store

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")
_STEMMER = snowballstemmer.stemmer("english")
_embedding_cache: Dict[str, List[float]] = {}


def stem_tokenize(text: str) -> set[str]:
    """Tokenize and stem so jam/jammed/printing/print share roots."""
    return {_STEMMER.stemWord(t) for t in _TOKEN_RE.findall(text.lower())}


def stemmed_jaccard(query: str, candidate: str) -> float:
    q, c = stem_tokenize(query), stem_tokenize(candidate)
    if not q or not c:
        return 0.0
    return len(q & c) / len(q | c)


def stemmed_jaccard_sets(query_stems: Set[str], candidate_stems: Set[str]) -> float:
    if not query_stems or not candidate_stems:
        return 0.0
    return len(query_stems & candidate_stems) / len(query_stems | candidate_stems)


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return max(0.0, dot / (na * nb))


@lru_cache(maxsize=256)
def _query_vec_cached(digest: str, text: str) -> Tuple[float, ...]:
    vec = GeminiClient().embed_text(text)
    if not vec:
        return tuple()
    return tuple(float(v) for v in vec)


def embed_query_cached(text: str) -> Optional[List[float]]:
    if not text.strip():
        return None
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cached = _query_vec_cached(digest, text)
    if not cached:
        return None
    return list(cached)


def clear_query_embedding_cache() -> None:
    _query_vec_cached.cache_clear()


def corpus_fingerprint(rows: Sequence[Tuple[str, str, ...]]) -> str:
    """Invalidate disk cache when corpus content or embed model changes."""
    settings = get_settings()
    digest = hashlib.sha256()
    digest.update(settings.gemini_model_embed.encode("utf-8"))
    for row in rows:
        digest.update(row[0].encode("utf-8"))
        digest.update(row[1].encode("utf-8"))
    return digest.hexdigest()[:24]


def _doc_vector(doc_id: str, doc: str, gemini: GeminiClient) -> Optional[List[float]]:
    cached = _embedding_cache.get(doc_id)
    if cached is not None:
        return cached

    store = get_embedding_cache_store()
    disk = store.get_vector(doc_id, doc)
    if disk:
        _embedding_cache[doc_id] = disk
        return disk

    dvec = gemini.embed_text(doc)
    if dvec:
        _embedding_cache[doc_id] = dvec
        store.put_vector(doc_id, doc, dvec)
    return dvec


def hydrate_corpus_embeddings_from_disk(rows: Sequence[Tuple[str, str, ...]]) -> int:
    """Load corpus vectors from disk into memory — instant, no API calls."""
    store = get_embedding_cache_store()
    store.bind_fingerprint(corpus_fingerprint(rows))
    loaded = 0
    for row in rows:
        doc_id, doc = row[0], row[1]
        if doc_id in _embedding_cache:
            continue
        vec = store.get_vector(doc_id, doc)
        if vec:
            _embedding_cache[doc_id] = vec
            loaded += 1
    return loaded


def warm_corpus_embedding_cache(rows: Sequence[Tuple[str, str, ...]]) -> int:
    """Pre-compute corpus vectors once — memory + disk — avoids per-ticket embed storms."""
    gemini = GeminiClient()
    if not gemini.available:
        return 0

    store = get_embedding_cache_store()
    store.bind_fingerprint(corpus_fingerprint(rows))

    warmed = 0
    for row in rows:
        doc_id, doc = row[0], row[1]
        if doc_id in _embedding_cache:
            continue
        if _doc_vector(doc_id, doc, gemini) is not None:
            warmed += 1
    store.flush()
    return warmed


def user_ticket_semantic_scores(
    query: str,
    tickets: Dict[str, str],
) -> Dict[str, float]:
    """
    Gemini embedding similarity for resolved user tickets.

    Always runs when candidates exist — keyword/BM25 scores alone can
    under-rank paraphrased repeats (e.g. Copilot integration tickets).
    """
    gemini = GeminiClient()
    if not gemini.available or not query.strip() or not tickets:
        return {}

    qvec = embed_query_cached(query)
    if not qvec:
        return {}

    scores: Dict[str, float] = {}
    for ticket_id, doc in tickets.items():
        if not doc.strip():
            continue
        dvec = _doc_vector(ticket_id, doc, gemini)
        if dvec:
            scores[ticket_id] = cosine_similarity(qvec, dvec)
    return scores


def corpus_semantic_scores(
    query: str,
    rows: Sequence[Tuple[str, str, ...]],
    *,
    doc_ids: set[str] | None = None,
) -> Dict[str, float]:
    """
    Gemini embedding cosine similarity against corpus documents.

    When doc_ids is set, only those candidates are embedded/scored (fast path).
    Vectors are cached in memory and on disk. Skipped when API key is missing.
    """
    gemini = GeminiClient()
    if not gemini.available or not query.strip():
        return {}

    qvec = embed_query_cached(query)
    if not qvec:
        return {}

    scores: Dict[str, float] = {}
    for row in rows:
        doc_id, doc = row[0], row[1]
        if doc_ids is not None and doc_id not in doc_ids:
            continue
        dvec = _doc_vector(doc_id, doc, gemini)
        if dvec:
            scores[doc_id] = cosine_similarity(qvec, dvec)
    return scores


def clear_embedding_cache() -> None:
    """Test helper — reset in-memory and in-process embedding caches."""
    _embedding_cache.clear()
    clear_query_embedding_cache()
    store = get_embedding_cache_store()
    store._entries.clear()
    store._dirty = False
