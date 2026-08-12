"""routers/public.py — the unauthenticated lead-capture endpoint. This is
the only endpoint in the whole app with no auth dependency at all, by
design: it's the public form a prospect fills in on the marketing site."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PublicLeadCreate, LeadOut
from app.services.lead_service import create_public_lead

router = APIRouter(prefix="/api/public", tags=["public"])


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def submit_lead(payload: PublicLeadCreate, db: Session = Depends(get_db)):
    lead = create_public_lead(db, payload)
    return _to_lead_out(lead)


def _to_lead_out(lead) -> LeadOut:
    return LeadOut(
        **{c.name: getattr(lead, c.name) for c in lead.__table__.columns},
        assigned_to_name=lead.assigned_to.full_name if lead.assigned_to else None,
    )
