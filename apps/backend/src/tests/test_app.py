"""Unit tests for backend microservice"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "backend"


def test_readiness_check(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_info_endpoint(client):
    resp = client.get("/api/v1/info")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "service" in data
    assert "gitops" in data
    assert data["gitops"]["managed_by"] == "ArgoCD"


def test_items_endpoint(client):
    resp = client.get("/api/v1/items")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert data["count"] == len(data["items"])


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"backend_requests_total" in resp.data


def test_404_handler(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == 404
