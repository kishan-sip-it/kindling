"""routers/users.py — admin manages member accounts."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserOut
from app.services.user_service import create_user, set_user_active, SelfDeactivationError
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


@router.patch("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user_endpoint(user_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    try:
        user = set_user_active(db, user_id, active=False, actor=admin)
    except SelfDeactivationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.patch("/{user_id}/reactivate", response_model=UserOut)
def reactivate_user_endpoint(user_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = set_user_active(db, user_id, active=True, actor=admin)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user
