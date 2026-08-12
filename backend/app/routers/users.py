"""routers/users.py — admin manages member accounts."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserOut
from app.services.user_service import create_user
from app.auth import require_admin, get_current_user
from app.models import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")
    return create_user(db, payload)


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    """Any authenticated user can see the team list — needed to populate
    the 'assign to' dropdown in the UI."""
    return db.query(User).order_by(User.full_name).all()
