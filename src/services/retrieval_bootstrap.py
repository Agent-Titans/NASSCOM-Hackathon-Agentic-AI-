"""Warm Chroma + embedding caches in the background (non-blocking for ticket submit)."""
from __future__ import annotations

import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

_warm_lock = threading.Lock()
_disk_thread: Optional[threading.Thread] = None
_api_thread: Optional[threading.Thread] = None
_warm_timer: Optional[threading.Timer] = None
_warm_scheduled = False
_disk_warm_done = False
_api_warm_done = False
_warm_error: Optional[str] = None
_warm_wants_api = False


def _run_disk_warm() -> int:
    """Index RAG corpus in Chroma and hydrate embeddings from disk."""
    from src.db.session import get_session_factory, init_db
    from src.services.ticket_retrieval import TicketRetrievalService

    from src.config.settings import get_settings

    init_db()
    Session = get_session_factory()
    with Session() as session:
        svc = TicketRetrievalService()
        if svc.chroma.available and svc.chroma.count > 0:
            svc.ensure_index(session)
            return svc.chroma.count
        settings = get_settings()
        if not settings.rag_auto_seed or settings.rag_corpus_mode.lower() == "synthetic":
            svc.ensure_index(session)
            return svc.chroma.count
        count = svc.index_corpus()
        if count == 0:
            svc.ensure_index(session)
            count = svc.chroma.count
        else:
            svc.ensure_index(session)
        return count


def _run_api_warm() -> int:
    """Fill embedding gaps via API (background only)."""
    from src.services.semantic_similarity import warm_corpus_embedding_cache
    from src.services.ticket_retrieval import _all_corpus_rows
    from src.stores.embedding_cache_store import get_embedding_cache_store

    rows = _all_corpus_rows()
    warmed = warm_corpus_embedding_cache(rows)
    get_embedding_cache_store().flush()
    return warmed


def _maybe_start_api_warm_locked() -> None:
    """Caller must hold _warm_lock."""
    global _api_thread
    if not _warm_wants_api or _api_warm_done or _warm_error:
        return
    if _api_thread is not None and _api_thread.is_alive():
        return
    _api_thread = threading.Thread(
        target=_api_worker,
        name="saarthi-retrieval-api-warm",
        daemon=True,
    )
    _api_thread.start()
    logger.info("Retrieval API warm started in background")


def _disk_worker() -> None:
    global _disk_warm_done, _warm_error
    try:
        count = _run_disk_warm()
        _disk_warm_done = True
        logger.info("Retrieval disk warm complete (chroma_docs=%s)", count)
        with _warm_lock:
            _maybe_start_api_warm_locked()
    except Exception as exc:
        _warm_error = str(exc)
        logger.exception("Retrieval disk warm failed")


def _api_worker() -> None:
    global _api_warm_done, _warm_error
    try:
        count = _run_api_warm()
        _api_warm_done = True
        logger.info("Retrieval API warm complete (api_embeds=%s)", count)
    except Exception as exc:
        _warm_error = str(exc)
        logger.exception("Retrieval API warm failed")


def _start_disk_warm() -> None:
    global _disk_thread
    with _warm_lock:
        if _disk_warm_done or _warm_error:
            _maybe_start_api_warm_locked()
            return
        if _disk_thread is not None and _disk_thread.is_alive():
            _maybe_start_api_warm_locked()
            return
        _disk_thread = threading.Thread(
            target=_disk_worker,
            name="saarthi-retrieval-disk-warm",
            daemon=True,
        )
        _disk_thread.start()
        logger.info("Retrieval disk warm started in background")


def start_retrieval_warm_background(*, delay_seconds: float = 2.0, api_embeds: bool = False) -> None:
    """Kick off warm once per process — delayed so the UI paints first."""
    global _warm_scheduled, _warm_timer, _warm_wants_api

    with _warm_lock:
        if api_embeds:
            _warm_wants_api = True
        if _disk_warm_done:
            if not _warm_wants_api or _api_warm_done:
                return
            _maybe_start_api_warm_locked()
            return
        if _disk_thread is not None and _disk_thread.is_alive():
            return
        if delay_seconds > 0 and _warm_scheduled:
            return
        _warm_scheduled = True

    if delay_seconds <= 0:
        with _warm_lock:
            if _warm_timer is not None:
                _warm_timer.cancel()
                _warm_timer = None
        _start_disk_warm()
        return

    _warm_timer = threading.Timer(delay_seconds, _start_disk_warm)
    _warm_timer.daemon = True
    _warm_timer.start()
    logger.info(
        "Retrieval warm scheduled in %.1fs (api_embeds=%s)",
        delay_seconds,
        api_embeds,
    )


def run_retrieval_warm(*, api_embeds: bool = True) -> None:
    """Blocking warm for scripts/CLI (`scripts/warm_cache.py`)."""
    global _disk_warm_done, _api_warm_done, _warm_wants_api
    if api_embeds:
        _warm_wants_api = True
    _run_disk_warm()
    _disk_warm_done = True
    if _warm_wants_api:
        _run_api_warm()
        _api_warm_done = True


def ensure_retrieval_warm(*, timeout: float = 12.0) -> bool:
    """Brief wait for disk index — never blocks on API embedding warm."""
    start_retrieval_warm_background(api_embeds=True, delay_seconds=0)

    if _disk_warm_done:
        return _warm_error is None

    thread = _disk_thread
    if thread is not None and thread.is_alive():
        thread.join(timeout=timeout)

    if _disk_warm_done:
        return _warm_error is None

    if thread is not None and thread.is_alive():
        logger.info("Disk warm still running after %.0fs — routing anyway", timeout)
        return True

    return _warm_error is None


def retrieval_warm_status() -> str:
    """idle | running | ready | error"""
    if _warm_error:
        return "error"
    if _disk_warm_done:
        return "ready"
    disk = _disk_thread
    api = _api_thread
    if (disk is not None and disk.is_alive()) or (api is not None and api.is_alive()):
        return "running"
    return "idle"
