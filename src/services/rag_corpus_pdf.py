"""Build a PDF catalog of all RAG corpus tickets."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fpdf import FPDF

from src.config.brand import PRODUCT_NAME
from src.data.rag_corpus_catalog import RagCatalogEntry, iter_rag_catalog_entries

_HAND_LABELS = {"1": "Hand 1 (Self-help)", "2": "Hand 2 (Team assist)", "3": "Hand 3 (Specialist)"}


def _safe(text: str) -> str:
    """FPDF core fonts are Latin-1 — replace unsupported characters."""
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


class _CorpusPDF(FPDF):
    def content_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 64, 175)
        self.cell(self.content_width(), 8, _safe(f"{PRODUCT_NAME} — RAG corpus reference"), align="L")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(self.content_width(), 8, _safe(f"Page {self.page_no()}"), align="C")


def build_rag_corpus_pdf(entries: list[RagCatalogEntry] | None = None) -> bytes:
    """Return PDF bytes for the full RAG ticket catalog."""
    items = entries if entries is not None else iter_rag_catalog_entries()
    pdf = _CorpusPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    w = pdf.content_width()
    pdf.multi_cell(
        w,
        5,
        _safe(
            f"This document lists all {len(items)} tickets and knowledge articles "
            f"indexed in the {PRODUCT_NAME} RAG corpus (ChromaDB + keyword retrieval). "
            "Each entry includes issue title, description, routing metadata, resolution steps, "
            "and citation references."
        ),
    )
    pdf.ln(4)

    for idx, entry in enumerate(items, start=1):
        if pdf.get_y() > 250:
            pdf.add_page()

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(w, 6, _safe(f"{idx}. {entry.title}"))
        pdf.ln(1)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(71, 85, 105)
        meta = (
            f"ID: {entry.ticket_id.upper()}  |  Source: {entry.source}  |  "
            f"Category: {entry.category}  |  Department: {entry.department}  |  "
            f"{_HAND_LABELS.get(entry.hand, entry.hand)}"
        )
        pdf.multi_cell(w, 4.5, _safe(meta))
        pdf.ln(2)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(w, 5, _safe("Description"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(w, 4.5, _safe(entry.description))
        pdf.ln(2)

        if entry.steps:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(w, 5, _safe("Resolution steps"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(51, 65, 85)
            for step_no, step in enumerate(entry.steps, start=1):
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w, 4.5, _safe(f"  {step_no}. {step}"))
            pdf.ln(1)

        if entry.citations:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(w, 5, _safe("References / citations"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(w, 4.5, _safe(", ".join(entry.citations)))
            pdf.ln(2)

        pdf.set_draw_color(226, 232, 240)
        y = pdf.get_y()
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(5)

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def write_rag_corpus_pdf(path: Path) -> int:
    """Write PDF to disk. Returns entry count."""
    entries = iter_rag_catalog_entries()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_rag_corpus_pdf(entries))
    return len(entries)
