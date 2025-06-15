def test_create_ticket(client):
    response = client.post("/tickets", json={
        "title": "Test Ticket",
        "description": "Testing ticket creation",
        "priority": "low"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Ticket"

def test_get_all_tickets(client):
    # Create one ticket
    client.post("/tickets", json={
        "title": "Another Ticket",
        "description": "Another test",
        "priority": "high"
    })
    # Get all
    response = client.get("/tickets")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_single_ticket(client):
    res = client.post("/tickets", json={
        "title": "Single Ticket",
        "description": "Get test",
        "priority": "medium"
    })
    ticket_id = res.get_json()["id"]

    get_res = client.get(f"/tickets/{ticket_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["title"] == "Single Ticket"

def test_update_ticket(client):
    res = client.post("/tickets", json={
        "title": "To Update",
        "description": "Initial",
        "priority": "low"
    })
    ticket_id = res.get_json()["id"]

    update_res = client.put(f"/tickets/{ticket_id}", json={
        "title": "Updated Title"
    })
    assert update_res.status_code == 200
    assert update_res.get_json()["title"] == "Updated Title"

def test_delete_ticket(client):
    res = client.post("/tickets", json={
        "title": "To Delete",
        "description": "Will be gone",
        "priority": "low"
    })
    ticket_id = res.get_json()["id"]

    del_res = client.delete(f"/tickets/{ticket_id}")
    assert del_res.status_code == 204
