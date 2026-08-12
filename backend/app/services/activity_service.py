"""
services/activity_service.py
-----------------------------
Small helper so every meaningful mutation on a lead writes one consistent
activity log row, instead of each router hand-rolling its own logging
(which is how audit trails quietly go inconsistent over time).
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import ActivityLog


def log_activity(db: Session, lead_id: UUID, action: str, detail: Optional[str] = None, actor_id: Optional[UUID] = None) -> ActivityLog:
    entry = ActivityLog(lead_id=lead_id, actor_id=actor_id, action=action, detail=detail)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
