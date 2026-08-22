from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_clinic_normal_intake():
    response = client.post("/api/intake", json={"domain":"clinic","message":"I have had a cough for three days and want an appointment."})
    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "clinic"
    assert data["escalation_required"] is False
    assert data["risk_level"] == "medium"


def test_clinic_emergency_escalation():
    response = client.post("/api/intake", json={"domain":"clinic","message":"I have severe chest pain and cannot breathe."})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "emergency"
    assert data["escalation_required"] is True


def test_legal_urgent():
    response = client.post("/api/intake", json={"domain":"legal","message":"I have a court hearing today and need help with my case."})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "high"
    assert data["escalation_required"] is True


def test_rejects_empty_message():
    response = client.post("/api/intake", json={"domain":"clinic","message":""})
    assert response.status_code == 422
