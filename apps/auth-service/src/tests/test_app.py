import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["service"] == "auth-service"

def test_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
