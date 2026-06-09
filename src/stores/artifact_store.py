"""Persist agent artifacts — one row per type per ticket."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from src.db.models import ClassificationArtifact, ResolutionArtifact, Ticket
from src.models.schemas import ClassificationResult, ResolutionResult
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
        row.low_grounding = result.low_grounding
        row.similarity_score = result.similarity_score
        self.session.commit()
