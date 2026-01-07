import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "participants" in data["Basketball"]

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Basketball/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@mergington.edu for Basketball" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Basketball"]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=duplicate@mergington.edu")
    # Second signup should fail
    response = client.post("/activities/Tennis%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]

def test_unregister_from_activity():
    # First signup
    client.post("/activities/Drama%20Club/signup?email=unregister@mergington.edu")
    # Then unregister
    response = client.post("/activities/Drama%20Club/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@mergington.edu from Drama Club" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Drama Club"]["participants"]

def test_unregister_activity_not_found():
    response = client.post("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up():
    response = client.post("/activities/Art%20Studio/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" in data["detail"]

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"