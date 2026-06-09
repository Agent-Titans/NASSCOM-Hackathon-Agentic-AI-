from __future__ import annotations

from sqlalchemy.orm import Session

from src.db.models import TicketComment, User


class CommentStore:
    def __init__(self, session: Session):
        self.session = session

    def add(self, ticket_id: str, user: User, body: str) -> TicketComment:
        row = TicketComment(
            ticket_id=ticket_id,
            user_id=user.user_id,
            author_role=user.role,
            body=body.strip(),
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def list_for_ticket(self, ticket_id: str) -> list[TicketComment]:
        return (
            self.session.query(TicketComment)
            .filter(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at.asc())
            .all()
        )
