"""API endpoint tests."""
from unittest.mock import AsyncMock, patch

import pytest


def test_root(client):
    """Root returns API info."""
    r = client.get("/")
    assert r.status_code == 200
    assert "docs" in r.json()
    assert "health" in r.json()


def test_health(client):
    """Health check returns DB status."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "database" in data


def test_webhook_order_requires_api_key(client):
    """Missing API key returns 422."""
    r = client.post(
        "/webhook/order",
        json={"order_id": "ORD-001", "amount": 100, "customer_name": "Test"},
    )
    assert r.status_code == 422


def test_webhook_order_invalid_api_key(client):
    """Invalid API key returns 401."""
    r = client.post(
        "/webhook/order",
        headers={"X-API-KEY": "wrong-key"},
        json={"order_id": "ORD-001", "amount": 100, "customer_name": "Test"},
    )
    assert r.status_code == 401


@patch("app.services.discord_service.httpx.AsyncClient")
def test_webhook_order_success(mock_client, client):
    """Valid order returns 200."""
    mock_response = type("Resp", (), {"is_success": True})()
    fake_client = AsyncMock()
    fake_client.post = AsyncMock(return_value=mock_response)
    mock_client.return_value.__aenter__ = AsyncMock(return_value=fake_client)
    mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
    r = client.post(
        "/webhook/order",
        headers={"X-API-KEY": "test-api-key"},
        json={"order_id": "ORD-TEST-001", "amount": 1500, "customer_name": "Alice"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "received"
    assert data["order_id"] == "ORD-TEST-001"
    assert "discord_alert_sent" in data


def test_webhook_order_invalid_amount(client):
    """Invalid amount returns 422."""
    r = client.post(
        "/webhook/order",
        headers={"X-API-KEY": "test-api-key"},
        json={"order_id": "ORD-001", "amount": -100, "customer_name": "Test"},
    )
    assert r.status_code == 422


def test_get_order_not_found(client):
    """Non-existent order returns 404."""
    r = client.get(
        "/orders/NONEXISTENT",
        headers={"X-API-KEY": "test-api-key"},
    )
    assert r.status_code == 404
