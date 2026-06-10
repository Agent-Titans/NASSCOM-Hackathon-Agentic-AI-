"""SQLAlchemy models — LLD ERD subset."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _id():
    return str(uuid.uuid4())[:8]


class User(Base):
    __tablename__ = "users"

    user_id = mapped_column(String(36), primary_key=True, default=_id)
    role = mapped_column(String(32), nullable=False)
    email = mapped_column(String(255), unique=True, nullable=False)
    department = mapped_column(String(64), nullable=True)

    tickets = relationship(
        "Ticket",
        back_populates="requester",
        foreign_keys="Ticket.user_id",
    )
    assigned_tickets = relationship(
        "Ticket",
        back_populates="assignee",
        foreign_keys="Ticket.assignee_id",
    )


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = mapped_column(String(36), primary_key=True, default=_id)
    user_id = mapped_column(ForeignKey("users.user_id"), nullable=False)
    assignee_id = mapped_column(ForeignKey("users.user_id"), nullable=True)
    title = mapped_column(String(255), nullable=False)
    description_raw = mapped_column(Text, nullable=False)
    description_sanitized = mapped_column(Text, nullable=True)
    urgency = mapped_column(String(16), default="medium")
    status = mapped_column(String(32), default="RECEIVED")
    hand = mapped_column(String(8), nullable=True)
    confidence = mapped_column(Float, nullable=True)
    department_queue = mapped_column(String(64), nullable=True)
    priority = mapped_column(String(8), nullable=True)
    sla_hours = mapped_column(Integer, nullable=True)
    escalation_required = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = relationship(
        "User",
        back_populates="tickets",
        foreign_keys=[user_id],
    )
    assignee = relationship(
        "User",
        back_populates="assigned_tickets",
        foreign_keys=[assignee_id],
    )
    audit_logs = relationship("AuditLog", back_populates="ticket")
    feedback = relationship("Feedback", back_populates="ticket")
    comments = relationship("TicketComment", back_populates="ticket", order_by="TicketComment.created_at")
    agent_runs = relationship("AgentRun", back_populates="ticket")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), nullable=False)
    event_type = mapped_column(String(64), nullable=False)
    agent = mapped_column(String(32), nullable=True)
    details = mapped_column(Text, nullable=True)
    duration_ms = mapped_column(Integer, nullable=True)
    timestamp = mapped_column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="audit_logs")


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    comment_id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    user_id = mapped_column(ForeignKey("users.user_id"), nullable=False)
    author_role = mapped_column(String(32), nullable=False)
    body = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), nullable=False)
    outcome = mapped_column(String(32), nullable=False)
    comments = mapped_column(Text, nullable=True)
    submitted_at = mapped_column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="feedback")


class AgentRun(Base):
    """Per-ticket pipeline run flags — LLD agent_runs table."""

    __tablename__ = "agent_runs"

    run_id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    guardrail_ok = mapped_column(Boolean, nullable=False, default=False)
    classification_ok = mapped_column(Boolean, nullable=False, default=False)
    routing_ok = mapped_column(Boolean, nullable=False, default=False)
    resolver_ok = mapped_column(Boolean, nullable=False, default=False)
    supervisor_ok = mapped_column(Boolean, nullable=False, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="agent_runs")


class ClassificationArtifact(Base):
    __tablename__ = "classification_artifacts"

    id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), unique=True)
    use_case_category = mapped_column(String(64), nullable=False)
    subcategory = mapped_column(String(64), nullable=True)
    confidence_hint = mapped_column(String(16), nullable=True)
    source = mapped_column(String(16), default="gemini")


class ResolutionArtifact(Base):
    __tablename__ = "resolution_artifacts"

    id = mapped_column(String(36), primary_key=True, default=_id)
    ticket_id = mapped_column(ForeignKey("tickets.ticket_id"), unique=True)
    steps_json = mapped_column(Text, default="[]")
    citations_json = mapped_column(Text, default="[]")
    references_json = mapped_column(Text, default="[]")
    low_grounding = mapped_column(Boolean, default=False)
    similarity_score = mapped_column(Float, nullable=True)
