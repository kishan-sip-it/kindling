"""
seed.py
-------
Creates one admin and one member demo account, and a couple of sample
leads, so the submitted deployment has working credentials to hand over
and isn't an empty database.

Run with: python seed.py
"""

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, init_db
from app.models import User, UserRole, Lead, LeadStatus
from app.auth import hash_password

ADMIN_EMAIL = "admin@leadflow.demo"
ADMIN_PASSWORD = "AdminDemo123!"
MEMBER_EMAIL = "member@leadflow.demo"
MEMBER_PASSWORD = "MemberDemo123!"


def run():
    init_db()
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == ADMIN_EMAIL).first():
            db.add(User(email=ADMIN_EMAIL, full_name="Ava Admin", hashed_password=hash_password(ADMIN_PASSWORD), role=UserRole.admin))
        if not db.query(User).filter(User.email == MEMBER_EMAIL).first():
            db.add(User(email=MEMBER_EMAIL, full_name="Max Member", hashed_password=hash_password(MEMBER_PASSWORD), role=UserRole.member))
        db.commit()

        if db.query(Lead).count() == 0:
            db.add_all([
                Lead(name="Priya Sharma", email="priya@example.com", company="Sharma Textiles", company_size="11-50", message="Interested in the Pro plan.", status=LeadStatus.new),
                Lead(name="Tom Reeves", email="tom@example.com", company="Reeves & Co", company_size="1-10", message="Can you call me tomorrow?", status=LeadStatus.contacted),
            ])
            db.commit()

        print("Seed complete.")
        print(f"Admin  → {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Member → {MEMBER_EMAIL} / {MEMBER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
