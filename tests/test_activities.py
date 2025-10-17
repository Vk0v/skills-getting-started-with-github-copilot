import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def client():
    # Use TestClient for synchronous tests against FastAPI
    with TestClient(app) as c:
        yield c


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Ensure it's a dict and contains an activity we know exists
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure not already registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    before = resp.json()[activity]["participants"]
    if email in before:
        # remove to have a clean state
        client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Signed up")

    # Confirm presence
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Unregistered")

    # Confirm removal
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]
