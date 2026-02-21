"""Integration tests for auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "test@veaf.org",
        "password": "Password123!",
        "nickname": "TestPilot",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@veaf.org",
        "password": "wrong",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
