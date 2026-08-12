"""
Core flow tests — the assignment requires at least 2 core flows covered.

Flow 1: public lead capture → shows up in the authenticated list.
Flow 2: the member permission model around assignment/status/notes.
"""


def test_public_lead_capture_flow(client, admin_token):
    """Flow 1: a prospect submits the public form (no auth), and it appears
    in the authenticated lead list with status 'new'."""
    resp = client.post(
        "/api/public/leads",
        json={"name": "Jordan Prospect", "email": "jordan@example.com", "company": "Prospect Co", "message": "Tell me more."},
    )
    assert resp.status_code == 201
    lead_id = resp.json()["id"]
    assert resp.json()["status"] == "new"
    assert resp.json()["assigned_to_id"] is None

    list_resp = client.get("/api/leads", headers={"Authorization": f"Bearer {admin_token}"})
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] >= 1
    assert any(item["id"] == lead_id for item in body["items"])


def test_member_can_self_claim_unassigned_lead(client, admin_token, member_token, member_user):
    create = client.post("/api/public/leads", json={"name": "Casey Prospect", "email": "casey@example.com"})
    lead_id = create.json()["id"]

    # Member self-claims the unassigned lead — should succeed.
    resp = client.patch(
        f"/api/leads/{lead_id}/assign",
        json={"assigned_to_id": str(member_user.id)},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["assigned_to_id"] == str(member_user.id)


def test_member_cannot_assign_lead_to_someone_else(client, member_token, member_user):
    create = client.post("/api/public/leads", json={"name": "Riley Prospect", "email": "riley@example.com"})
    lead_id = create.json()["id"]

    other_user_id = "00000000-0000-0000-0000-000000000000"
    resp = client.patch(
        f"/api/leads/{lead_id}/assign",
        json={"assigned_to_id": other_user_id},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_member_cannot_update_status_on_lead_not_assigned_to_them(client, member_token):
    create = client.post("/api/public/leads", json={"name": "Unassigned Prospect", "email": "u@example.com"})
    lead_id = create.json()["id"]

    resp = client.patch(
        f"/api/leads/{lead_id}/status",
        json={"status": "contacted"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_member_can_update_status_and_add_note_on_own_lead(client, member_token, member_user):
    create = client.post("/api/public/leads", json={"name": "Own Prospect", "email": "own@example.com"})
    lead_id = create.json()["id"]

    client.patch(
        f"/api/leads/{lead_id}/assign",
        json={"assigned_to_id": str(member_user.id)},
        headers={"Authorization": f"Bearer {member_token}"},
    )

    status_resp = client.patch(
        f"/api/leads/{lead_id}/status",
        json={"status": "qualified"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "qualified"

    note_resp = client.post(
        f"/api/leads/{lead_id}/notes",
        json={"content": "Had a great first call."},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert note_resp.status_code == 201

    detail = client.get(f"/api/leads/{lead_id}", headers={"Authorization": f"Bearer {member_token}"})
    assert len(detail.json()["notes"]) == 1
    # Activity trail should now have: created, assigned, status_changed, note_added
    assert len(detail.json()["activity"]) == 4


def test_admin_can_update_any_lead_regardless_of_assignment(client, admin_token):
    create = client.post("/api/public/leads", json={"name": "Admin Test Prospect", "email": "admintest@example.com"})
    lead_id = create.json()["id"]

    resp = client.patch(
        f"/api/leads/{lead_id}/status",
        json={"status": "won"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "won"


def test_pagination_and_filtering(client, admin_token):
    for i in range(5):
        client.post("/api/public/leads", json={"name": f"Bulk {i}", "email": f"bulk{i}@example.com"})

    resp = client.get("/api/leads?page=1&page_size=2", headers={"Authorization": f"Bearer {admin_token}"})
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["total"] >= 5

    search_resp = client.get("/api/leads?search=Bulk+3", headers={"Authorization": f"Bearer {admin_token}"})
    assert any("Bulk 3" in item["name"] for item in search_resp.json()["items"])
