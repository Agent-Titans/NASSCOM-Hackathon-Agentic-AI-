"""Semantic + stemmed RAG retrieval — jam/jammed printer cases."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.rag_demo_corpus import RAG_DEMO_CORPUS, corpus_search_document
from src.services.rag_gate import evaluate_rag_match
from src.services.semantic_similarity import clear_embedding_cache, stem_tokenize
from src.services.ticket_retrieval import TicketRetrievalService, _keyword_overlap

_KB_PRINTER_DOC = "Printer print toner paper jam hardware"


def _rag_h1_07_doc() -> str:
    for entry in RAG_DEMO_CORPUS:
        if entry[0] == "rag-h1-07":
            return corpus_search_document(entry)
    raise AssertionError("rag-h1-07 missing")


def test_stemming_collapses_jam_and_jammed():
    stems = stem_tokenize("paper jammed in printer")
    assert "jam" in stems
    assert "jamm" not in stems


def test_printer_jam_kb_seed_passes_minimum_keyword_gate():
    query = "Printer paper jammed in 2nd floor printer in office"
    score = _keyword_overlap(query, _KB_PRINTER_DOC)
    assert score >= 0.28, f"kb-hw-014 keyword overlap too low: {score}"


def test_title_in_retrieval_text_boosts_rag_h1_07():
    body = "Printer paper jammed in 2nd floor printer in office"
    title = "Printer paper jammed"
    combined = f"{title}\n{body}"
    doc = _rag_h1_07_doc()
    assert _keyword_overlap(combined, doc) >= _keyword_overlap(body, doc)


def test_printer_jam_trusted_with_mock_embeddings():
    from src.db.session import get_session_factory, init_db

    query = "Printer paper jammed\nPrinter paper jammed in 2nd floor printer in office"
    init_db()
    Session = get_session_factory()

    clear_embedding_cache()
    query_vec = [1.0, 0.0, 0.0]
    rag_vec = [0.95, 0.05, 0.0]
    kb_vec = [0.7, 0.71, 0.0]

    def fake_embed(text: str):
        if "print jobs stuck" in text or "floor 3" in text:
            return rag_vec
        if _KB_PRINTER_DOC in text:
            return kb_vec
        if text.strip() == query.strip():
            return query_vec
        return [0.0, 0.0, 1.0]

    class _NoChroma:
        available = False
        count = 0

    with Session() as session:
        with patch("src.services.semantic_similarity.GeminiClient") as mock_cls:
            mock_cls.return_value.available = True
            mock_cls.return_value.embed_text.side_effect = fake_embed
            raw = TicketRetrievalService(chroma=_NoChroma()).find_similar(session, query)

    assert raw is not None
    assert raw.ticket_id in ("rag-h1-07", "kb-hw-014")
    assert raw.source_hand == "1"
    gate = evaluate_rag_match(raw)
    assert gate.trusted is not None
    assert gate.reason == "trusted"
    assert raw.similarity_score >= 0.55
