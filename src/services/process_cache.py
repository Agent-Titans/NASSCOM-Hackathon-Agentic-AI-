"""Process-wide caches with explicit invalidation — safe for routing correctness."""
from __future__ import annotations

import hashlib
from typing import Dict, Optional

# Bumped when resolved tickets or feedback change retrieval/historical inputs.
_cache_generation = 0

# Short-lived retrieval candidate cache (same text → same scores until invalidated).
_retrieval_cache: Dict[str, dict[str, float]] = {}
_RETRIEVAL_CACHE_MAX = 128

_historical_cache: Dict[str, float] = {}


def cache_generation() -> int:
    return _cache_generation


def invalidate_retrieval_cache() -> None:
    """Call when Chroma user-ticket index or resolved pool may have changed."""
    global _cache_generation, _retrieval_cache
    _cache_generation += 1
    _retrieval_cache.clear()


def invalidate_historical_cache() -> None:
    _historical_cache.clear()


def invalidate_process_caches() -> None:
    invalidate_retrieval_cache()
    invalidate_historical_cache()
    clear_query_embedding_cache()


def retrieval_cache_key(text: str, exclude_ticket_id: Optional[str]) -> str:
    payload = f"{_cache_generation}|{exclude_ticket_id or ''}|{text.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_retrieval_candidates(key: str) -> Optional[dict[str, float]]:
    return _retrieval_cache.get(key)


def set_retrieval_candidates(key: str, candidates: dict[str, float]) -> None:
    if len(_retrieval_cache) >= _RETRIEVAL_CACHE_MAX:
        _retrieval_cache.pop(next(iter(_retrieval_cache)))
    _retrieval_cache[key] = dict(candidates)


def get_historical_rate(category: str) -> Optional[float]:
    return _historical_cache.get(category)


def set_historical_rate(category: str, rate: float) -> None:
    _historical_cache[category] = rate


def clear_query_embedding_cache() -> None:
    from src.services.semantic_similarity import clear_query_embedding_cache as _clear

    _clear()
