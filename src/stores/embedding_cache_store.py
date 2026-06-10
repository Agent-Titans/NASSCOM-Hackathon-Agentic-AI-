"""Persistent on-disk cache for Gemini document embedding vectors."""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

_CACHE_VERSION = 1


def _cache_path() -> Path:
    return get_settings().embedding_cache_path


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def load_disk_cache(*, fingerprint: str) -> Dict[str, Dict[str, object]]:
    path = _cache_path()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Embedding cache read failed (%s) — rebuilding", exc)
        return {}
    if raw.get("version") != _CACHE_VERSION or raw.get("fingerprint") != fingerprint:
        return {}
    entries = raw.get("entries")
    return entries if isinstance(entries, dict) else {}


def save_disk_cache(
    entries: Dict[str, Dict[str, object]],
    *,
    fingerprint: str,
) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": _CACHE_VERSION,
        "fingerprint": fingerprint,
        "entries": entries,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    tmp.replace(path)


class EmbeddingCacheStore:
    """In-memory + disk cache for corpus and resolved-ticket document vectors."""

    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, object]] = {}
        self._fingerprint = ""
        self._dirty = False

    def bind_fingerprint(self, fingerprint: str) -> None:
        if self._fingerprint == fingerprint and self._entries:
            return
        self._fingerprint = fingerprint
        self._entries = load_disk_cache(fingerprint=fingerprint)
        self._dirty = False
        if self._entries:
            logger.info("Loaded %d cached embedding vectors from disk", len(self._entries))

    def get_vector(self, doc_id: str, text: str) -> Optional[List[float]]:
        row = self._entries.get(doc_id)
        if not row:
            return None
        if row.get("content_hash") != content_hash(text):
            return None
        values = row.get("vector")
        if not isinstance(values, list):
            return None
        return [float(v) for v in values]

    def put_vector(self, doc_id: str, text: str, vector: List[float]) -> None:
        self._entries[doc_id] = {
            "content_hash": content_hash(text),
            "vector": vector,
        }
        self._dirty = True

    def flush(self) -> None:
        if not self._dirty or not self._fingerprint:
            return
        save_disk_cache(self._entries, fingerprint=self._fingerprint)
        self._dirty = False


_store = EmbeddingCacheStore()


def get_embedding_cache_store() -> EmbeddingCacheStore:
    return _store
