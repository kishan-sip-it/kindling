"""
routers/leads.py
------------------
Authenticated lead endpoints. Every handler here is intentionally thin:
parse the request, call a service function, translate the result (or a
PermissionDenied/NotFound exception) into an HTTP response. All the actual
rules live in services/lead_service.py.
"""

import math
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, LeadStatus
from app.schemas import (
    LeadOut, LeadDetailOut, PaginatedLeads, LeadStatusUpdate, LeadAssignUpdate,
    NoteCreate, NoteOut, ActivityOut,
)
from app.services import lead_service
from app.services.lead_service import PermissionDenied, NotFound
from app.auth import get_current_user

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _lead_out(lead) -> LeadOut:
    return LeadOut(
        id=lead.id, name=lead.name, email=lead.email, phone=lead.phone,
        company=lead.company, company_size=lead.company_size, message=lead.message,
        source=lead.source, status=lead.status, assigned_to_id=lead.assigned_to_id,
        assigned_to_name=lead.assigned_to.full_name if lead.assigned_to else None,
        created_at=lead.created_at, updated_at=lead.updated_at,
    )


def _lead_detail_out(lead) -> LeadDetailOut:
    base = _lead_out(lead)
    notes = [
        NoteOut(id=n.id, content=n.content, author_id=n.author_id, author_name=n.author.full_name if n.author else None, created_at=n.created_at)
        for n in lead.notes
    ]
    activity = [
        ActivityOut(id=a.id, action=a.action, detail=a.detail, actor_id=a.actor_id, actor_name=a.actor.full_name if a.actor else None, created_at=a.created_at)
        for a in lead.activity
    ]
    return LeadDetailOut(**base.model_dump(), notes=notes, activity=activity)


@router.get("", response_model=PaginatedLeads)
def list_leads(
    status_filter: Optional[LeadStatus] = Query(None, alias="status"),
    assigned_to_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    items, total = lead_service.list_leads(db, status_filter, assigned_to_id, search, page, page_size)
    return PaginatedLeads(
        items=[_lead_out(l) for l in items],
        total=total, page=page, page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/{lead_id}", response_model=LeadDetailOut)
def get_lead(lead_id: UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    try:
        lead = lead_service.get_lead_or_raise(db, lead_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _lead_detail_out(lead)


@router.patch("/{lead_id}/status", response_model=LeadOut)
def update_status(lead_id: UUID, payload: LeadStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        lead = lead_service.get_lead_or_raise(db, lead_id)
        lead = lead_service.update_status(db, lead, payload.status, user)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDenied as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return _lead_out(lead)


@router.patch("/{lead_id}/assign", response_model=LeadOut)
def assign_lead(lead_id: UUID, payload: LeadAssignUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        lead = lead_service.get_lead_or_raise(db, lead_id)
        lead = lead_service.assign_lead(db, lead, payload.assigned_to_id, user)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDenied as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return _lead_out(lead)


@router.post("/{lead_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def add_note(lead_id: UUID, payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        lead = lead_service.get_lead_or_raise(db, lead_id)
        note = lead_service.add_note(db, lead, payload.content, user)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDenied as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return NoteOut(id=note.id, content=note.content, author_id=note.author_id, author_name=user.full_name, created_at=note.created_at)
