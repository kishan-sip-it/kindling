"""Auth rule tests — the assignment explicitly requires tests covering auth rules."""


def test_login_succeeds_with_correct_credentials(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "admin"
    assert "access_token" in body


def test_login_fails_with_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong-password"})
    assert resp.status_code == 401


def test_login_fails_for_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "whatever"})
    assert resp.status_code == 401


def test_protected_endpoint_rejects_missing_token(client):
    resp = client.get("/api/leads")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    resp = client.get("/api/leads", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_member_cannot_create_users(client, member_token):
    """Only admins may create new user accounts — server-side enforced."""
    resp = client.post(
        "/api/users",
        json={"email": "new@test.com", "full_name": "New Person", "password": "password123", "role": "member"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_admin_can_create_users(client, admin_token):
    resp = client.post(
        "/api/users",
        json={"email": "new@test.com", "full_name": "New Person", "password": "password123", "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@test.com"
