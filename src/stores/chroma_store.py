"""ChromaDB store — local sentence-transformers or Gemini embeddings for RAG."""
from __future__ import annotations

import logging
from typing import Any, Optional

import chromadb

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

_COLLECTION = "historical_tickets"


def _local_embedding_function():
    """ONNX all-MiniLM-L6-v2 — same family as sentence-transformers, no PyTorch."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    return DefaultEmbeddingFunction()


class ChromaTicketStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection: Optional[Any] = None
        self._embedding_mode = "none"
        self._open_existing_collection()

    def _open_existing_collection(self) -> bool:
        try:
            backend = get_settings().rag_embedding_backend.lower()
            if backend == "local":
                self._collection = self._client.get_collection(
                    _COLLECTION,
                    embedding_function=_local_embedding_function(),
                )
            else:
                self._collection = self._client.get_collection(_COLLECTION)
            meta = self._collection.metadata or {}
            self._embedding_mode = str(meta.get("embedding_mode", "existing"))
            return True
        except Exception:
            self._collection = None
            self._embedding_mode = "none"
            return False

    @property
    def available(self) -> bool:
        return self._collection is not None

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
        *,
        embedding: Optional[list[float]] = None,
    ) -> None:
        if not self._collection:
            return
        try:
            if embedding is not None:
                self._collection.upsert(
                    ids=[ticket_id],
                    documents=[document],
                    metadatas=[metadata],
                    embeddings=[embedding],
                )
            else:
                self._collection.upsert(
                    ids=[ticket_id],
                    documents=[document],
                    metadatas=[metadata],
                )
        except Exception as exc:
            logger.warning("Chroma upsert failed: %s", exc)

    def reset_collection(self) -> bool:
        """Delete and recreate collection for the configured embedding backend."""
        settings = get_settings()
        backend = settings.rag_embedding_backend.lower()
        try:
            try:
                self._client.delete_collection(_COLLECTION)
            except Exception:
                pass

            if backend == "local":
                self._collection = self._client.create_collection(
                    name=_COLLECTION,
                    embedding_function=_local_embedding_function(),
                    metadata={
                        "hnsw:space": "cosine",
                        "embedding_mode": "local",
                        "embedding_model": settings.local_embedding_model,
                    },
                )
                self._embedding_mode = "local"
            else:
                self._collection = self._client.create_collection(
                    name=_COLLECTION,
                    metadata={
                        "hnsw:space": "cosine",
                        "embedding_mode": "gemini",
                        "embedding_model": settings.gemini_model_embed,
                    },
                )
                self._embedding_mode = "gemini"
            return True
        except Exception as exc:
            logger.warning("Chroma collection create failed (%s)", exc)
            self._collection = None
            self._embedding_mode = "none"
            return False

    def reset_gemini_collection(self) -> bool:
        """Backward-compatible alias — respects rag_embedding_backend."""
        return self.reset_collection()

    def upsert_document_batch(
        self,
        entries: list[tuple[str, str, dict[str, Any]]],
    ) -> None:
        if not self._collection or not entries:
            return
        batch_size = 100
        for start in range(0, len(entries), batch_size):
            chunk = entries[start : start + batch_size]
            try:
                self._collection.upsert(
                    ids=[doc_id for doc_id, _doc, _meta in chunk],
                    documents=[doc for _doc_id, doc, _meta in chunk],
                    metadatas=[meta for _doc_id, _doc, meta in chunk],
                )
            except Exception as exc:
                logger.warning("Chroma document batch upsert failed (%s)", exc)
                for doc_id, doc, meta in chunk:
                    self.upsert(doc_id, doc, meta)

    def upsert_gemini_batch(
        self,
        entries: list[tuple[str, str, dict[str, Any], list[float]]],
    ) -> None:
        if not self._collection or not entries:
            return
        batch_size = 100
        for start in range(0, len(entries), batch_size):
            chunk = entries[start : start + batch_size]
            try:
                self._collection.upsert(
                    ids=[doc_id for doc_id, _doc, _meta, _vec in chunk],
                    documents=[doc for _doc_id, doc, _meta, _vec in chunk],
                    metadatas=[meta for _doc_id, _doc, meta, _vec in chunk],
                    embeddings=[vec for _doc_id, _doc, _meta, vec in chunk],
                )
            except Exception as exc:
                logger.warning("Chroma gemini batch upsert failed (%s)", exc)
                for doc_id, doc, meta, vec in chunk:
                    self.upsert(doc_id, doc, meta, embedding=vec)

    def reindex_documents(self, entries: list[tuple[str, str, dict[str, Any]]]) -> int:
        """Index corpus with local sentence-transformers (no API calls)."""
        if not self.reset_collection():
            return 0
        self.upsert_document_batch(entries)
        return self.count

    def reindex_gemini(
        self,
        entries: list[tuple[str, str, dict[str, Any], list[float]]],
    ) -> int:
        """Replace collection with Gemini-precomputed embeddings."""
        if not self.reset_collection():
            return 0
        self.upsert_gemini_batch(entries)
        return self.count

    def reindex_all(
        self,
        entries: list[tuple[str, str, dict[str, Any]]],
    ) -> int:
        settings = get_settings()
        if settings.rag_embedding_backend.lower() == "gemini":
            from src.services.chroma_indexing import embed_corpus_entries

            embedded = embed_corpus_entries(entries)
            return self.reindex_gemini(embedded)
        return self.reindex_documents(entries)

    def query(self, text: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Return (ticket_id, similarity_score) best first."""
        if not self._collection or self.count == 0 or not text.strip():
            return []

        try:
            if self._embedding_mode == "gemini":
                from src.services.semantic_similarity import embed_query_cached

                vec = embed_query_cached(text[:8000])
                if not vec:
                    return []
                result = self._collection.query(
                    query_embeddings=[vec],
                    n_results=min(top_k, self.count),
                )
            else:
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
            if self._embedding_mode in ("gemini", "local"):
                sim = max(0.0, 1.0 - float(dist))
            else:
                sim = 1.0 / (1.0 + float(dist))
            ranked.append((tid, sim))
        ranked.sort(key=lambda x: -x[1])
        return ranked
