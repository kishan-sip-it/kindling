import os
os.environ["JWT_SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User, UserRole
from app.auth import hash_password

# A single shared in-memory SQLite connection for the whole test session —
# StaticPool keeps the same connection alive across requests instead of
# each `get_db()` call getting a fresh (and therefore empty) in-memory DB.
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    return TestingSessionLocal()


@pytest.fixture
def admin_user(db_session):
    user = User(email="admin@test.com", full_name="Admin Test", hashed_password=hash_password("password123"), role=UserRole.admin)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def member_user(db_session):
    user = User(email="member@test.com", full_name="Member Test", hashed_password=hash_password("password123"), role=UserRole.member)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    return resp.json()["access_token"]


@pytest.fixture
def member_token(client, member_user):
    resp = client.post("/api/auth/login", json={"email": "member@test.com", "password": "password123"})
    return resp.json()["access_token"]
