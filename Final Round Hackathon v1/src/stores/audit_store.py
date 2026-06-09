from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from src.db.models import AuditLog, Ticket


class AuditLogStore:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        ticket: Ticket,
        event_type: str,
        *,
        agent: Optional[str] = None,
        details: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> AuditLog:
        row = AuditLog(
            ticket_id=ticket.ticket_id,
            event_type=event_type,
            agent=agent,
            details=details,
            duration_ms=duration_ms,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def list_for_ticket(self, ticket_id: str) -> list[AuditLog]:
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.ticket_id == ticket_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )
