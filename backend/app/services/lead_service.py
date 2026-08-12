"""
services/lead_service.py
--------------------------
All lead business logic and permission rules live here — the routers in
routers/leads.py only parse the request, call one of these functions, and
translate the result/exception into an HTTP response. This is the exact
separation Task B's own assessment argues for: these functions are unit
tested directly (see tests/test_leads.py) with no HTTP server involved.

Permission rules (not specified by the brief beyond "two roles" — this is
the concrete policy chosen and documented):
  - Admin: full access to every lead; can assign a lead to any member.
  - Member: can view every lead (team visibility); can only change status
    or add notes on leads assigned to them; can self-claim an unassigned
    lead, but cannot assign a lead to a different member.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus, Note, User, UserRole
from app.schemas import PublicLeadCreate
from app.services.activity_service import log_activity


class PermissionDenied(Exception):
    """Raised for a business-rule permission violation. Routers translate
    this to HTTP 403 — kept as a plain exception here so this module has
    no dependency on FastAPI and can be unit tested standalone."""
    pass


class NotFound(Exception):
    pass


def create_public_lead(db: Session, data: PublicLeadCreate) -> Lead:
    lead = Lead(
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        company_size=data.company_size,
        message=data.message,
        source="website",
        status=LeadStatus.new,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    log_activity(db, lead.id, action="created", detail="Submitted via public capture form", actor_id=None)
    return lead


def list_leads(
    db: Session,
    status_filter: Optional[LeadStatus] = None,
    assigned_to_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Lead], int]:
    query = db.query(Lead)

    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if assigned_to_id:
        query = query.filter(Lead.assigned_to_id == assigned_to_id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Lead.name.ilike(like), Lead.email.ilike(like), Lead.company.ilike(like)))

    total = query.count()
    items = (
        query.order_by(Lead.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_lead_or_raise(db: Session, lead_id: UUID) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise NotFound(f"Lead {lead_id} not found")
    return lead


def _can_modify(lead: Lead, actor: User) -> bool:
    if actor.role == UserRole.admin:
        return True
    return lead.assigned_to_id == actor.id


def update_status(db: Session, lead: Lead, new_status: LeadStatus, actor: User) -> Lead:
    if not _can_modify(lead, actor):
        raise PermissionDenied("You can only update leads assigned to you.")

    old_status = lead.status
    lead.status = new_status
    db.commit()
    db.refresh(lead)
    log_activity(
        db, lead.id, action="status_changed",
        detail=f"{old_status.value} → {new_status.value}", actor_id=actor.id,
    )
    return lead


def assign_lead(db: Session, lead: Lead, target_user_id: Optional[UUID], actor: User) -> Lead:
    if actor.role == UserRole.admin:
        pass  # admins may assign to anyone, or unassign (target_user_id=None)
    else:
        # Members may only self-claim a currently-unassigned lead.
        if lead.assigned_to_id is not None:
            raise PermissionDenied("This lead is already assigned — only an admin can reassign it.")
        if target_user_id != actor.id:
            raise PermissionDenied("Members can only assign leads to themselves.")

    lead.assigned_to_id = target_user_id
    db.commit()
    db.refresh(lead)
    log_activity(
        db, lead.id, action="assigned",
        detail=f"Assigned to {target_user_id}" if target_user_id else "Unassigned",
        actor_id=actor.id,
    )
    return lead


def add_note(db: Session, lead: Lead, content: str, actor: User) -> Note:
    if not _can_modify(lead, actor):
        raise PermissionDenied("You can only add notes to leads assigned to you.")

    note = Note(lead_id=lead.id, author_id=actor.id, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    log_activity(db, lead.id, action="note_added", detail=content[:120], actor_id=actor.id)
    return note
