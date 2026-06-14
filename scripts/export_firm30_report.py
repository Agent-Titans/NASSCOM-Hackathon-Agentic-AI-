#!/usr/bin/env python3
"""Export firm30 routing report JSON to CSV and PDF."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fpdf import FPDF  # noqa: E402

from src.config.brand import PRODUCT_NAME  # noqa: E402

CSV_FIELDS = [
    "ticket_id",
    "title",
    "description",
    "expected_department",
    "actual_department",
    "department_correct",
    "expected_category",
    "actual_category",
    "category_correct",
    "actual_hand",
    "actual_hand_label",
    "expected_hand",
    "hand_correct",
    "confidence",
    "classifier_source",
    "classifier_confidence_hint",
    "policy_trigger",
    "routing_reason",
    "rag_score",
    "rag_match_id",
    "latency_sec",
]


def _safe(text: str) -> str:
    return (
        str(text)
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def export_csv(payload: dict, out_path: Path) -> None:
    rows = payload["results"]
    with out_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class _ReportPDF(FPDF):
    def content_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 64, 175)
        self.cell(
            self.content_width(),
            8,
            _safe(f"{PRODUCT_NAME} - Firm 30 Routing Report"),
            align="L",
        )
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(self.content_width(), 8, _safe(f"Page {self.page_no()}"), align="C")


def export_pdf(payload: dict, out_path: Path) -> None:
    summary = payload["summary"]
    results = payload["results"]
    pdf = _ReportPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    w = pdf.content_width()

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w, 8, _safe("Summary"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)
    lines = [
        f"Tickets routed: {summary['total']}",
        f"Department accuracy: {summary['department_correct']}/{summary['total']} "
        f"({summary['department_accuracy_pct']:.1f}%)",
        f"Category accuracy: {summary['category_correct']}/{summary['total']} "
        f"({summary['category_accuracy_pct']:.1f}%)",
        f"Hand accuracy: {summary['hand_correct']}/{summary['total']} "
        f"({summary['hand_accuracy_pct']:.1f}%)",
        "Hand distribution: "
        + ", ".join(
            f"Hand {hand}={count}"
            for hand, count in sorted(summary["hand_distribution"].items())
        ),
    ]
    for line in lines:
        pdf.multi_cell(w, 5, _safe(line))
    pdf.ln(4)

    if summary.get("mismatches"):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(180, 50, 50)
        pdf.cell(w, 6, _safe("Department mismatches"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        for m in summary["mismatches"]:
            pdf.multi_cell(
                w,
                4.5,
                _safe(
                    f"- {m['ticket_id']}: expected {m['expected']}, "
                    f"got {m['actual']} (conf {m['confidence']:.3f})"
                ),
            )
        pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w, 8, _safe("Per-ticket routing"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for row in results:
        if pdf.get_y() > 175:
            pdf.add_page()

        ok = "OK" if row["department_correct"] else "MISMATCH"
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(
            w,
            5,
            _safe(f"{row['ticket_id']} [{ok}] - {row['title']}"),
        )
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(71, 85, 105)
        meta = (
            f"Hand: {row['actual_hand_label']} (H{row['actual_hand']}) | "
            f"Team: {row['actual_department']} (expected {row['expected_department']}) | "
            f"Category: {row['actual_category']} | Confidence: {row['confidence']:.3f} | "
            f"Classifier: {row['classifier_source']} ({row['classifier_confidence_hint']})"
        )
        pdf.multi_cell(w, 4, _safe(meta))
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(w, 4, _safe(f"Description: {row['description'][:220]}"))
        pdf.ln(1)
        pdf.multi_cell(w, 4, _safe(f"Reason: {row['routing_reason']}"))
        pdf.ln(3)

    pdf.output(str(out_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Export firm30 routing report.")
    parser.add_argument(
        "--json",
        type=Path,
        default=ROOT / "docs" / "firm30_routing_report.json",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=ROOT / "docs" / "firm30_routing_report.csv",
    )
    parser.add_argument(
        "--pdf-out",
        type=Path,
        default=ROOT / "docs" / "firm30_routing_report.pdf",
    )
    args = parser.parse_args()

    if not args.json.exists():
        print(f"JSON report not found: {args.json}", file=sys.stderr)
        print("Run: python scripts/firm30_routing_report.py", file=sys.stderr)
        return 1

    payload = json.loads(args.json.read_text(encoding="utf-8"))
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    export_csv(payload, args.csv_out)
    export_pdf(payload, args.pdf_out)

    print(f"CSV: {args.csv_out}")
    print(f"PDF: {args.pdf_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
