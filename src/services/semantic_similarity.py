"""Stemmed tokens + Gemini embedding cosine similarity for RAG retrieval."""
from __future__ import annotations

import math
import re
from typing import Dict, List, Sequence, Tuple

import snowballstemmer

from src.clients.gemini_client import GeminiClient

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


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return max(0.0, dot / (na * nb))


def corpus_semantic_scores(
    query: str,
    rows: Sequence[Tuple[str, str, ...]],
) -> Dict[str, float]:
    """
    Gemini embedding cosine similarity against corpus documents.

    Caches corpus vectors in-process. Skipped when API key is missing.
    """
    gemini = GeminiClient()
    if not gemini.available or not query.strip():
        return {}

    qvec = gemini.embed_text(query)
    if not qvec:
        return {}

    scores: Dict[str, float] = {}
    for row in rows:
        doc_id, doc = row[0], row[1]
        dvec = _embedding_cache.get(doc_id)
        if dvec is None:
            dvec = gemini.embed_text(doc)
            if dvec:
                _embedding_cache[doc_id] = dvec
        if dvec:
            scores[doc_id] = cosine_similarity(qvec, dvec)
    return scores


def clear_embedding_cache() -> None:
    """Test helper — reset cached corpus vectors."""
    _embedding_cache.clear()
