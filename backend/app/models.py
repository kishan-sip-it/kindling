"""
models.py
---------
Data model for the lead management app.

- User: admin or member, with hashed password.
- Lead: the core entity — status pipeline + optional assignment to a User.
- Note: timestamped notes a user adds to a lead.
- ActivityLog: an append-only audit trail — every status change, assignment
  change, and note addition writes a row here automatically (see
  services/activity_service.py), so "who did what, when" is always answerable
  without reconstructing it from other tables.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum, TypeDecorator, CHAR, Boolean, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class GUID(TypeDecorator):
    """Portable UUID-as-string column — stores as CHAR(36) on any backend
    (SQLite for tests, Postgres in production) instead of relying on
    postgresql.UUID, which SQLite can't create tables with. Values are
    always plain str(uuid.uuid4()) so both dialects behave identically."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value


class UserRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    won = "won"
    lost = "lost"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.member)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_leads = relationship("Lead", back_populates="assigned_to", foreign_keys="Lead.assigned_to_id")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)  # original inquiry text from the public capture form
    source = Column(String(100), default="website")
    status = Column(SAEnum(LeadStatus), nullable=False, default=LeadStatus.new, index=True)

    assigned_to_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", back_populates="assigned_leads", foreign_keys=[assigned_to_id])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = relationship("Note", back_populates="lead", cascade="all, delete-orphan", order_by="Note.created_at.desc()")
    activity = relationship("ActivityLog", back_populates="lead", cascade="all, delete-orphan", order_by="ActivityLog.created_at.desc()")


class Note(Base):
    __tablename__ = "notes"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(GUID(), ForeignKey("leads.id"), nullable=False)
    author_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="notes")
    author = relationship("User")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(GUID(), ForeignKey("leads.id"), nullable=False)
    actor_id = Column(GUID(), ForeignKey("users.id"), nullable=True)  # null for the public form itself
    action = Column(String(100), nullable=False)  # "created" | "status_changed" | "assigned" | "note_added"
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="activity")
    actor = relationship("User")
