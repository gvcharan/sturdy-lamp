import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    # Accept both redirect and final page (if testclient follows redirect)
    if response.history:
        # Redirect happened
        assert response.history[0].status_code in (302, 307)
        assert str(response.url).endswith("/static/index.html")
    else:
        # No redirect, should be the static page
        assert response.status_code == 200

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_for_activity_success():
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    # Remove if already present
    client.delete(f"/activities/{activity}/unregister", params={"email": email})
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Clean up
    client.delete(f"/activities/{activity}/unregister", params={"email": email})

def test_signup_for_activity_duplicate():
    email = "michael@mergington.edu"
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_from_activity_success():
    email = "tempuser@mergington.edu"
    activity = "Programming Class"
    # Ensure user is signed up
    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 200
    assert f"Unregistered {email} from {activity}" in response.json()["message"]

def test_unregister_from_activity_not_registered():
    email = "notregistered@mergington.edu"
    activity = "Programming Class"
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_from_activity_not_found():
    response = client.delete("/activities/Nonexistent/unregister", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
