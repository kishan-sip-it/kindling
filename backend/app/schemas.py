"""schemas.py — request/response models for the API."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole, LeadStatus


# --- Auth ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: UserRole = UserRole.member


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


# --- Leads ---

class PublicLeadCreate(BaseModel):
    """What the public, unauthenticated capture form submits."""
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    company_size: Optional[str] = None
    message: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadAssignUpdate(BaseModel):
    assigned_to_id: Optional[UUID] = None  # null = unassign


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: UUID
    content: str
    author_id: UUID
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityOut(BaseModel):
    id: UUID
    action: str
    detail: Optional[str] = None
    actor_id: Optional[UUID] = None
    actor_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    company_size: Optional[str] = None
    message: Optional[str] = None
    source: str
    status: LeadStatus
    assigned_to_id: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetailOut(LeadOut):
    notes: List[NoteOut] = []
    activity: List[ActivityOut] = []


class PaginatedLeads(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    page_size: int
    total_pages: int
