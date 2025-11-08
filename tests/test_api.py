from pathlib import Path
import sys

# Ensure the src directory is on path so we can import the app module
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from fastapi.testclient import TestClient

import app as app_module


client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should be a mapping and include known activity keys
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "test_student@example.com"

    # ensure test email not present initially
    if test_email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(test_email)

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert test_email in app_module.activities[activity]["participants"]

    # trying to sign up again should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp2.status_code == 400

    # unregister
    resp3 = client.post(f"/activities/{activity}/unregister?email={test_email}")
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert "Unregistered" in body3.get("message", "")
    assert test_email not in app_module.activities[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    fake_email = "no_one@nowhere.example"
    # ensure not present
    if fake_email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(fake_email)

    resp = client.post(f"/activities/{activity}/unregister?email={fake_email}")
    assert resp.status_code == 404
