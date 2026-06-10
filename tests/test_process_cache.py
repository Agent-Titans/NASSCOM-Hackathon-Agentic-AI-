"""Process cache invalidation — routing inputs stay fresh after resolve."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services.process_cache import (
    cache_generation,
    get_retrieval_candidates,
    invalidate_process_caches,
    retrieval_cache_key,
    set_retrieval_candidates,
)


def test_retrieval_cache_invalidates_on_bump():
    text = "vpn login issue"
    key = retrieval_cache_key(text, None)
    set_retrieval_candidates(key, {"rag-h1-04": 0.9})
    assert get_retrieval_candidates(key) == {"rag-h1-04": 0.9}

    before = cache_generation()
    invalidate_process_caches()
    assert cache_generation() == before + 1

    new_key = retrieval_cache_key(text, None)
    assert new_key != key
    assert get_retrieval_candidates(key) is None
    assert get_retrieval_candidates(new_key) is None
