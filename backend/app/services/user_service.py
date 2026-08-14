"""services/user_service.py — user creation, authentication, and deactivation."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.auth import hash_password, verify_password


class SelfDeactivationError(Exception):
    """Raised when an admin tries to deactivate their own account — kept
    HTTP-agnostic for the same reason as lead_service's exceptions."""
    pass


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verifies credentials only — does NOT check is_active. The router
    checks that separately so a deactivated account gets a specific
    'account deactivated' message instead of being indistinguishable from
    a wrong password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def set_user_active(db: Session, target_user_id: UUID, active: bool, actor: User) -> User:
    """Deactivate/reactivate an account. Deactivating instead of deleting
    preserves the user's existing leads, notes, and activity history —
    hard-deleting would orphan or cascade-delete records other people
    still need to see (e.g. a lead's activity trail should still show who
    did what, even after that person leaves the team)."""
    if str(target_user_id) == str(actor.id) and not active:
        raise SelfDeactivationError("You can't deactivate your own account.")

    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        return None
    user.is_active = active
    db.commit()
    db.refresh(user)
    return user
