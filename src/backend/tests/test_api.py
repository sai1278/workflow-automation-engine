# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_info():
    r = client.get("/info")
    assert r.status_code == 200
    j = r.json()
    assert "version" in j and "environment" in j

def test_data_and_metrics():
    # /data endpoint
    r = client.get("/data")
    assert r.status_code == 200
    assert "data" in r.json()

    # /metrics endpoint
    m = client.get("/metrics")
    assert m.status_code == 200
    assert "app_data_requests_total" in m.text  # Prometheus counter
