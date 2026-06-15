#!/usr/bin/env python3
"""Export docs/SAARTHI_BUSINESS_DOCUMENTATION to PDF.

Tries (in order): Chrome headless, Playwright, fpdf2 from markdown.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "SAARTHI_BUSINESS_DOCUMENTATION.html"
MD = ROOT / "docs" / "SAARTHI_BUSINESS_DOCUMENTATION.md"
PDF = ROOT / "docs" / "SAARTHI_BUSINESS_DOCUMENTATION.pdf"

CHROME_PATHS = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
]

FONT_CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]


def _export_chrome() -> bool:
    if not HTML.exists():
        return False
    for chrome in CHROME_PATHS:
        if not chrome.exists():
            continue
        cmd = [
            str(chrome),
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={PDF}",
            f"file://{HTML.resolve()}",
        ]
        print(f"Exporting via {chrome.name}...")
        subprocess.run(cmd, check=True, capture_output=True)
        return PDF.exists()
    return False


def _export_playwright() -> bool:
    if not HTML.exists():
        return False
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(HTML.resolve().as_uri(), wait_until="networkidle")
            page.pdf(
                path=str(PDF),
                format="A4",
                print_background=True,
                margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
            )
            browser.close()
    except Exception:
        return False
    return PDF.exists()


def _find_font() -> Path | None:
    for path in FONT_CANDIDATES:
        if path.exists():
            return path
    return None


def _ascii_safe(text: str) -> str:
    return (
        text.replace("\u2014", " - ")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2192", "->")
        .replace("\u00b7", " - ")
        .replace("\u00a9", "(c)")
    )


def _export_fpdf() -> bool:
    if not MD.exists():
        return False
    from fpdf import FPDF

    font_path = _find_font()
    if font_path is None:
        print("No Unicode TTF found for fpdf2 export.")
        return False

    class DocPDF(FPDF):
        def header(self) -> None:
            if self.page_no() > 1:
                self.set_font("Body", "", 8)
                self.set_text_color(100, 116, 139)
                self.cell(0, 8, "SAARTHI - Business Documentation | Nasscom Agentic AI Hackathon 2026", align="C", new_x="LMARGIN", new_y="NEXT")

        def footer(self) -> None:
            self.set_y(-12)
            self.set_font("Body", "", 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 8, f"Page {self.page_no()}", align="C")

        def section_title(self, text: str) -> None:
            self.ln(4)
            self.set_font("Body", "B", 13)
            self.set_text_color(3, 105, 161)
            self.multi_cell(0, 7, text)
            self.set_draw_color(226, 232, 240)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

        def sub_title(self, text: str) -> None:
            self.ln(2)
            self.set_font("Body", "B", 11)
            self.set_text_color(15, 23, 42)
            self.multi_cell(0, 6, text)
            self.ln(1)

        def body_text(self, text: str) -> None:
            self.set_font("Body", "", 10)
            self.set_text_color(71, 85, 105)
            self.multi_cell(0, 5, text)
            self.ln(1)

        def bullet(self, text: str) -> None:
            self.set_font("Body", "", 10)
            self.set_text_color(71, 85, 105)
            x = self.get_x()
            self.cell(5, 5, "-")
            self.multi_cell(0, 5, text)
            self.set_x(x)

    pdf = DocPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Body", "", str(font_path))
    pdf.add_font("Body", "B", str(font_path))
    pdf.add_font("Body", "I", str(font_path))
    pdf.add_page()

    pdf.set_fill_color(12, 74, 110)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_y(55)
    pdf.set_font("Body", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, "NASSCOM AGENTIC AI HACKATHON 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Body", "B", 40)
    pdf.cell(0, 16, "SAARTHI", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Body", "", 15)
    pdf.cell(0, 9, "Intelligent IT Service Management", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Body", "", 11)
    pdf.multi_cell(0, 6, "Business and Technical Overview\nClassify, Route, Resolve with Agentic AI", align="C")
    pdf.set_y(198)
    pdf.set_font("Body", "", 9)
    pdf.multi_cell(0, 5, "Use Case 1 - Enterprise IT Incident Triage\nDocument v1.0 - June 2026 - Confidential", align="C")
    pdf.set_y(228)
    pdf.set_font("Body", "I", 9)
    pdf.set_text_color(251, 191, 36)
    pdf.multi_cell(
        0,
        5,
        "AI-assisted development: Built with Cursor / LLM pair-programming under human review, "
        "architecture governance, and structured test validation.",
        align="C",
    )
    pdf.add_page()

    lines = _ascii_safe(MD.read_text(encoding="utf-8")).splitlines()
    i = 0
    in_table = False
    table_rows: list[list[str]] = []

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            return
        col_count = max(len(r) for r in table_rows)
        w = 190 / col_count
        for ri, row in enumerate(table_rows):
            if ri == 1 and all(set(c.strip()) <= set("-:") for c in row):
                continue
            pdf.set_font("Body", "B" if ri == 0 else "", 8)
            for cell in row:
                pdf.cell(w, 6, cell.strip()[:48], border=1, fill=(ri == 0))
            pdf.ln()
        pdf.ln(2)
        table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("|") and "|" in line[1:]:
            in_table = True
            table_rows.append([c.strip() for c in line.strip("|").split("|")])
            i += 1
            continue
        if in_table:
            flush_table()
        if line.startswith("## "):
            pdf.section_title(line[3:].strip())
        elif line.startswith("### "):
            pdf.sub_title(line[4:].strip())
        elif line.startswith("> "):
            pdf.set_font("Body", "I", 9)
            pdf.set_text_color(3, 105, 161)
            pdf.multi_cell(0, 5, line[2:].strip())
            pdf.ln(1)
        elif line.startswith("- ") or line.startswith("* "):
            pdf.bullet(line[2:].strip())
        elif line.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            pdf.set_font("Body", "", 8)
            pdf.set_text_color(30, 41, 59)
            pdf.set_fill_color(241, 245, 249)
            pdf.multi_cell(0, 4, "\n".join(code_lines), fill=True)
            pdf.ln(2)
        elif line.strip() == "---":
            pdf.ln(2)
        elif line.strip() and not line.startswith("# "):
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            text = re.sub(r"`(.+?)`", r"\1", text)
            pdf.body_text(text)
        i += 1

    flush_table()
    pdf.output(str(PDF))
    return PDF.exists()


def main() -> int:
    if _export_chrome():
        print(f"Wrote {PDF}")
        return 0
    if _export_playwright():
        print(f"Wrote {PDF} (Playwright)")
        return 0
    if _export_fpdf():
        print(f"Wrote {PDF} (fpdf2)")
        return 0

    print("Could not auto-export PDF. Manual option:")
    print(f"  open '{HTML}'")
    print("  File -> Print -> Save as PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
