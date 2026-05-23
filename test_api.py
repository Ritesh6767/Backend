import os

from fastapi.testclient import TestClient

from app import database, models
from app.main import app

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "enquiries.db")


def setup_module(module):
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    models.Base.metadata.create_all(bind=database.engine)


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_history_flow():
    client = TestClient(app)
    payload = {
        "channel": "WhatsApp",
        "customer_name": "Amit Verma",
        "message": "I want to book a demo session for this weekend.",
    }
    create_resp = client.post("/enquiry", json=payload)
    assert create_resp.status_code == 202
    body = create_resp.json()
    assert body["status"] == "queued"
    job_id = body["job_id"]

    history_resp = client.get(f"/enquiry/{job_id}/history")
    assert history_resp.status_code == 200
    data = history_resp.json()
    assert data["id"] == job_id
    assert data["status"] in ["open", "processed"]
    assert data["history"]


def test_schedule_follow_up():
    client = TestClient(app)
    payload = {
        "channel": "email",
        "customer_name": "Nisha",
        "message": "Can you share the price list?",
    }
    create_resp = client.post("/enquiry", json=payload)
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]

    follow_up_payload = {"delay_minutes": 10, "message_template": "Hi Nisha, following up on your enquiry."}
    response = client.post(f"/enquiry/{job_id}/follow-up", json=follow_up_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Follow-up scheduled"


def test_escalate_enquiry():
    client = TestClient(app)
    payload = {
        "channel": "call",
        "customer_name": "Karan",
        "message": "I need help with a problem that is not solved.",
    }
    create_resp = client.post("/enquiry", json=payload)
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]

    escalate_payload = {"reason": "Customer explicitly requested human agent."}
    response = client.post(f"/enquiry/{job_id}/escalate", json=escalate_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Enquiry escalated"

    history_resp = client.get(f"/enquiry/{job_id}/history")
    assert history_resp.status_code == 200
    assert history_resp.json()["status"] == "escalated"
