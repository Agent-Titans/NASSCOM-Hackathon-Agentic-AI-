"""ChromaDB store — BM25 keyword retrieval over historical tickets (LLD RAG)."""
from __future__ import annotations

import logging
from typing import Any, Optional

import chromadb

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

_COLLECTION = "historical_tickets"


def _bm25_embedding_function():
    try:
        from chromadb.utils.embedding_functions import ChromaBm25EmbeddingFunction

        return ChromaBm25EmbeddingFunction()
    except (ImportError, ValueError) as exc:
        logger.warning("Chroma BM25 unavailable (%s)", exc)
        return None


def _default_embedding_function():
    try:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        return DefaultEmbeddingFunction()
    except (ImportError, ValueError) as exc:
        logger.warning("Chroma default embedding unavailable (%s)", exc)
        return None


class ChromaTicketStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._ef: Optional[Any] = None
        self._collection: Optional[Any] = None
        self._bm25_broken = False
        self._embedding_mode = "none"

        if self._open_existing_collection():
            return

        self._ef = _bm25_embedding_function()
        if self._ef is not None:
            try:
                self._collection = self._client.create_collection(
                    name=_COLLECTION,
                    embedding_function=self._ef,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                self._collection = None
            if self._collection and self._probe_collection():
                self._embedding_mode = "bm25"
                return
        self._try_default_embedding()

    def _open_existing_collection(self) -> bool:
        """Reuse persisted collection (avoids BM25 vs default embedding conflicts)."""
        try:
            self._collection = self._client.get_collection(_COLLECTION)
            self._embedding_mode = "existing"
            self._bm25_broken = False
            return True
        except Exception:
            return False

    def _probe_collection(self) -> bool:
        """Return True when upsert/query works on the active collection."""
        if not self._collection:
            return False
        probe_id = "__chroma_probe__"
        try:
            self._collection.upsert(
                ids=[probe_id],
                documents=["probe keyword test document"],
                metadatas=[{"probe": True}],
            )
            self._collection.delete(ids=[probe_id])
            return True
        except Exception as exc:
            logger.warning("Chroma collection probe failed (%s)", exc)
            self._bm25_broken = True
            self._collection = None
            return False

    def _try_default_embedding(self) -> None:
        """BM25 sparse vectors fail on Chroma 1.5.x — fall back to dense default embeddings."""
        default_ef = _default_embedding_function()
        if default_ef is None:
            return
        try:
            try:
                self._client.delete_collection(_COLLECTION)
            except Exception:
                pass
            self._ef = default_ef
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION,
                embedding_function=self._ef,
            )
            if self._probe_collection():
                self._embedding_mode = "default"
                self._bm25_broken = False
                logger.info("Chroma using default dense embeddings (BM25 unavailable)")
        except Exception as exc:
            logger.warning("Chroma default embedding setup failed (%s)", exc)
            self._collection = None

    @property
    def available(self) -> bool:
        return self._collection is not None and not self._bm25_broken

    @property
    def count(self) -> int:
        if not self._collection:
            return 0
        return self._collection.count()

    def upsert(
        self,
        ticket_id: str,
        document: str,
        metadata: dict[str, Any],
    ) -> None:
        if not self._collection:
            return
        try:
            self._collection.upsert(
                ids=[ticket_id],
                documents=[document],
                metadatas=[metadata],
            )
        except Exception as exc:
            logger.warning("Chroma upsert failed: %s", exc)

    def reindex_all(
        self,
        entries: list[tuple[str, str, dict[str, Any]]],
    ) -> int:
        """Replace collection contents with corpus entries. Returns document count."""
        if not self.available and self._embedding_mode == "none":
            default_ef = _default_embedding_function()
            if default_ef:
                self._ef = default_ef
                try:
                    try:
                        self._client.delete_collection(_COLLECTION)
                    except Exception:
                        pass
                    self._collection = self._client.create_collection(
                        name=_COLLECTION,
                        embedding_function=self._ef,
                    )
                    self._embedding_mode = "default"
                    self._bm25_broken = False
                except Exception as exc:
                    logger.warning("Chroma reindex setup failed (%s)", exc)
                    return 0

        if not self._collection:
            return 0

        try:
            try:
                self._client.delete_collection(_COLLECTION)
            except Exception:
                pass
            self._collection = self._client.create_collection(
                name=_COLLECTION,
                embedding_function=self._ef,
            )
        except Exception as exc:
            logger.warning("Chroma reindex recreate failed (%s)", exc)
            return 0

        for doc_id, document, metadata in entries:
            self.upsert(doc_id, document, metadata)
        return self.count

    def query(self, text: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Return (ticket_id, similarity_score) best first. similarity in 0..1."""
        if not self._collection or self.count == 0 or not text.strip():
            return []
        try:
            result = self._collection.query(
                query_texts=[text[:8000]],
                n_results=min(top_k, self.count),
            )
        except Exception as exc:
            logger.warning("Chroma query failed: %s", exc)
            return []

        ids = (result.get("ids") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        if not ids:
            return []

        ranked: list[tuple[str, float]] = []
        for tid, dist in zip(ids, distances):
            if dist is None:
                continue
            sim = 1.0 / (1.0 + float(dist))
            ranked.append((tid, sim))
        ranked.sort(key=lambda x: -x[1])
        return ranked
