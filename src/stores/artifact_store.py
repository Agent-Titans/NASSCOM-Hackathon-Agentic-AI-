"""Persist agent artifacts — one row per type per ticket."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket
from src.models.schemas import ClassificationResult, ResolutionResult, RetrievalReference
from src.services.reference_ticket_loader import resolve_reference_label
from src.services.resolution_steps_codec import encode_steps


class ArtifactStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_classification(self, ticket: Ticket, result: ClassificationResult) -> None:
        row = (
            self.session.query(ClassificationArtifact)
            .filter(ClassificationArtifact.ticket_id == ticket.ticket_id)
            .first()
        )
        if row is None:
            row = ClassificationArtifact(ticket_id=ticket.ticket_id)
            self.session.add(row)
        row.use_case_category = result.use_case_category
        row.subcategory = result.subcategory
        row.confidence_hint = result.confidence_hint
        row.source = result.source
        self.session.commit()

    def save_resolution(self, ticket: Ticket, result: ResolutionResult) -> None:
        row = (
            self.session.query(ResolutionArtifact)
            .filter(ResolutionArtifact.ticket_id == ticket.ticket_id)
            .first()
        )
        if row is None:
            row = ResolutionArtifact(ticket_id=ticket.ticket_id)
            self.session.add(row)
        row.steps_json = encode_steps(
            result.steps,
            steps_requester=result.steps_requester,
            steps_assignee=result.steps_assignee,
        )
        row.citations_json = json.dumps(result.citations)
        row.references_json = json.dumps(
            [ref.to_dict() for ref in result.references]
        )
        row.low_grounding = result.low_grounding
        row.similarity_score = result.similarity_score
        self.session.commit()

    @staticmethod
    def load_references(row: ResolutionArtifact | None) -> list[RetrievalReference]:
        if not row:
            return []
        raw = row.references_json if hasattr(row, "references_json") else None
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list) and parsed:
                    return [RetrievalReference.from_dict(item) for item in parsed]
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        try:
            legacy = json.loads(row.citations_json or "[]")
        except json.JSONDecodeError:
            return []
        if not isinstance(legacy, list):
            return []
        refs: list[RetrievalReference] = []
        seen: set[str] = set()
        for cite in legacy:
            if not isinstance(cite, str) or not cite.strip():
                continue
            ticket_id = resolve_reference_label(cite)
            if not ticket_id or ticket_id in seen:
                continue
            seen.add(ticket_id)
            refs.append(
                RetrievalReference(
                    ticket_id=ticket_id,
                    label=cite,
                    score=float(row.similarity_score or 0.0),
                    source="rag",
                )
            )
        return refs
