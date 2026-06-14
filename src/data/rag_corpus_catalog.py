"""Unified catalog of every document in the SAARTHI RAG corpus."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from src.data.enterprise_rag_corpus import ENTERPRISE_RAG_CORPUS
from src.config.departments import CATEGORY_TO_DEPARTMENT
from src.data.rag_demo_corpus import (
    RAG_DEMO_CORPUS,
    RagDemoEntry,
    demo_ticket_routing,
)
from src.data.kb_seed_corpus import KB_SEED_CORPUS

_SOURCE_KB = "KB seed"
_SOURCE_DEMO = "RAG demo"
_SOURCE_ENTERPRISE = "Enterprise RAG"

_CORPUS_PREFIXES = ("rag-", "kb-", "ent-")


def is_corpus_ticket_id(ticket_id: str | None) -> bool:
    """True when ticket_id is a RAG/KB/enterprise seed row (not a live user ticket)."""
    tid = (ticket_id or "").strip().lower()
    return tid.startswith(_CORPUS_PREFIXES)


@lru_cache(maxsize=1)
def citation_label_to_ticket_id() -> dict[str, str]:
    """
    Map display citations (KB-DB-DEDUP, RAG-H3-09) to owning corpus ticket_id.
    Secondary KB labels are not standalone tickets — they point at a playbook row.
    """
    index: dict[str, str] = {}
    for entry in iter_rag_catalog_entries():
        tid = entry.ticket_id.lower()
        index[tid.upper()] = tid
        index[entry.ticket_id.upper()] = tid
        for cite in entry.citations:
            index[cite.upper()] = tid
    return index


@dataclass(frozen=True)
class RagCatalogEntry:
    ticket_id: str
    title: str
    description: str
    category: str
    hand: str
    department: str
    steps: tuple[str, ...]
    citations: tuple[str, ...]
    source: str


def _department_for(entry: RagDemoEntry) -> str:
    doc_id, _title, _desc, category, hand, _steps, _cites = entry
    if doc_id.startswith("rag-") or doc_id.startswith("ent-"):
        return str(demo_ticket_routing(doc_id, category, hand)["department_queue"])
    return CATEGORY_TO_DEPARTMENT.get(category, category)


def _from_demo_entry(entry: RagDemoEntry, *, source: str) -> RagCatalogEntry:
    doc_id, title, description, category, hand, steps, cites = entry
    return RagCatalogEntry(
        ticket_id=doc_id,
        title=title,
        description=description,
        category=category,
        hand=hand,
        department=_department_for(entry),
        steps=tuple(steps),
        citations=tuple(cites),
        source=source,
    )


def iter_rag_catalog_entries() -> list[RagCatalogEntry]:
    """All KB seeds + demo corpus + enterprise corpus, stable sort order."""
    rows: list[RagCatalogEntry] = []

    for seed_id, doc, category, steps, cites in KB_SEED_CORPUS:
        rows.append(
            RagCatalogEntry(
                ticket_id=seed_id,
                title=f"KB knowledge article ({seed_id.upper()})",
                description=doc,
                category=category,
                hand="1",
                department=CATEGORY_TO_DEPARTMENT.get(category, category),
                steps=tuple(steps),
                citations=tuple(cites),
                source=_SOURCE_KB,
            )
        )

    for entry in RAG_DEMO_CORPUS:
        rows.append(_from_demo_entry(entry, source=_SOURCE_DEMO))

    for entry in ENTERPRISE_RAG_CORPUS:
        rows.append(_from_demo_entry(entry, source=_SOURCE_ENTERPRISE))

    return rows
