"""Build Gemini embedding vectors for ChromaDB ingest (LLD RAG corpus)."""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Callable, Optional

from src.clients.gemini_client import GeminiClient
from src.config.settings import get_settings
from src.stores.embedding_cache_store import get_embedding_cache_store

logger = logging.getLogger(__name__)

_API_BATCH = 20


def _entries_fingerprint(entries: list[tuple[str, str, dict]]) -> str:
    digest = hashlib.sha256()
    digest.update(get_settings().gemini_model_embed.encode("utf-8"))
    for doc_id, doc, _meta in entries:
        digest.update(doc_id.encode("utf-8"))
        digest.update(doc.encode("utf-8"))
    return digest.hexdigest()[:24]


def embed_corpus_entries(
    entries: list[tuple[str, str, dict]],
    *,
    batch_size: int = 25,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> list[tuple[str, str, dict, list[float]]]:
    """
    Return (id, document, metadata, embedding_vector) for each entry.
    Uses Gemini batchEmbedContents + persistent disk cache.
    """
    if not entries:
        return []

    gemini = GeminiClient()
    if not gemini.available:
        raise RuntimeError(
            "GOOGLE_API_KEY required for Chroma Gemini indexing. Set it in .env"
        )

    fingerprint = _entries_fingerprint(entries)
    cache = get_embedding_cache_store()
    cache.bind_fingerprint(fingerprint)

    out: list[tuple[str, str, dict, list[float]]] = []
    total = len(entries)
    pending: list[tuple[int, str, str, dict]] = []

    for i, (doc_id, doc, meta) in enumerate(entries):
        vec = cache.get_vector(doc_id, doc)
        if vec is not None:
            out.append((doc_id, doc, meta, vec))
            continue
        pending.append((i, doc_id, doc, meta))

    done = len(out)

    for start in range(0, len(pending), _API_BATCH):
        chunk = pending[start : start + _API_BATCH]
        texts = [doc for _i, _id, doc, _meta in chunk]
        vectors = gemini.embed_texts_batch(texts)
        if not vectors or all(v is None for v in vectors):
            vectors = [gemini.embed_text(doc) for _i, _id, doc, _meta in chunk]

        for (idx, doc_id, doc, meta), vec in zip(chunk, vectors):
            if not vec:
                logger.warning("Skip Chroma doc %s — embedding failed", doc_id)
                continue
            cache.put_vector(doc_id, doc, vec)
            out.append((doc_id, doc, meta, vec))
            done += 1

        cache.flush()
        time.sleep(0.15)
        if on_progress:
            on_progress(done, total)

    cache.flush()
    return out
