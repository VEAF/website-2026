"""Integration tests for auth endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.utils.cache import discord_oauth_states
from tests.factories import UserFactory


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
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_api_info(client: AsyncClient):
    # WHEN
    response = await client.get("/api")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "VEAF Website API"
    assert "version" in data
    assert "description" in data


# --- Discord OAuth2 Tests ---

DISCORD_USER_RESPONSE = {
    "id": "123456789012345678",
    "username": "testpilot",
    "global_name": "Test Pilot",
    "email": "discord@veaf.org",
    "verified": True,
}


def _mock_httpx_post(token_status=200):
    """Create a mock for httpx token exchange (json() is sync in httpx)."""
    mock_resp = MagicMock()
    mock_resp.status_code = token_status
    mock_resp.json.return_value = {"access_token": "discord_token_123", "token_type": "Bearer"}
    return mock_resp


def _mock_httpx_get(user_data=None, user_status=200):
    """Create a mock for httpx user info fetch (json() is sync in httpx)."""
    mock_resp = MagicMock()
    mock_resp.status_code = user_status
    mock_resp.json.return_value = user_data or DISCORD_USER_RESPONSE
    return mock_resp


@pytest.mark.asyncio
async def test_discord_authorize_returns_url(client: AsyncClient):
    # GIVEN
    original = settings.DISCORD_CLIENT_ID
    settings.DISCORD_CLIENT_ID = "test-client-id"

    # WHEN
    response = await client.get("/api/auth/discord/authorize")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "discord.com/oauth2/authorize" in data["authorization_url"]
    assert "client_id=test-client-id" in data["authorization_url"]
    assert "scope=identify+email" in data["authorization_url"]

    settings.DISCORD_CLIENT_ID = original


@pytest.mark.asyncio
async def test_discord_authorize_disabled_without_config(client: AsyncClient):
    # GIVEN
    original = settings.DISCORD_CLIENT_ID
    settings.DISCORD_CLIENT_ID = ""

    # WHEN
    response = await client.get("/api/auth/discord/authorize")

    # THEN
    assert response.status_code == 501

    settings.DISCORD_CLIENT_ID = original


@pytest.mark.asyncio
async def test_discord_callback_invalid_state(client: AsyncClient):
    # WHEN
    response = await client.post("/api/auth/discord/callback", json={
        "code": "some_code",
        "state": "invalid_state",
    })

    # THEN
    assert response.status_code == 400
    assert "state" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_discord_callback_creates_new_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    state = "test-state-new-user"
    discord_oauth_states[state] = True

    original_id = settings.DISCORD_CLIENT_ID
    original_secret = settings.DISCORD_CLIENT_SECRET
    settings.DISCORD_CLIENT_ID = "test-client-id"
    settings.DISCORD_CLIENT_SECRET = "test-secret"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=_mock_httpx_post())
    mock_client.get = AsyncMock(return_value=_mock_httpx_get())

    # WHEN
    with patch("app.api.auth.httpx.AsyncClient", return_value=mock_client):
        response = await client.post("/api/auth/discord/callback", json={
            "code": "auth_code_123",
            "state": state,
        })

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify state was consumed
    assert state not in discord_oauth_states

    settings.DISCORD_CLIENT_ID = original_id
    settings.DISCORD_CLIENT_SECRET = original_secret


@pytest.mark.asyncio
async def test_discord_callback_links_existing_user_by_email(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = UserFactory(email="discord@veaf.org", nickname="ExistingPilot")
    db_session.add(user)
    await db_session.flush()

    state = "test-state-link"
    discord_oauth_states[state] = True

    original_id = settings.DISCORD_CLIENT_ID
    original_secret = settings.DISCORD_CLIENT_SECRET
    settings.DISCORD_CLIENT_ID = "test-client-id"
    settings.DISCORD_CLIENT_SECRET = "test-secret"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=_mock_httpx_post())
    mock_client.get = AsyncMock(return_value=_mock_httpx_get())

    # WHEN
    with patch("app.api.auth.httpx.AsyncClient", return_value=mock_client):
        response = await client.post("/api/auth/discord/callback", json={
            "code": "auth_code_123",
            "state": state,
        })

    # THEN
    assert response.status_code == 200
    await db_session.refresh(user)
    assert user.discord_id == "123456789012345678"
    assert user.discord == "Test Pilot"

    settings.DISCORD_CLIENT_ID = original_id
    settings.DISCORD_CLIENT_SECRET = original_secret


@pytest.mark.asyncio
async def test_discord_callback_logs_in_existing_linked_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = UserFactory(email="linked@veaf.org", nickname="LinkedPilot", discord_id="123456789012345678")
    db_session.add(user)
    await db_session.flush()

    state = "test-state-existing"
    discord_oauth_states[state] = True

    original_id = settings.DISCORD_CLIENT_ID
    original_secret = settings.DISCORD_CLIENT_SECRET
    settings.DISCORD_CLIENT_ID = "test-client-id"
    settings.DISCORD_CLIENT_SECRET = "test-secret"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=_mock_httpx_post())
    mock_client.get = AsyncMock(return_value=_mock_httpx_get())

    # WHEN
    with patch("app.api.auth.httpx.AsyncClient", return_value=mock_client):
        response = await client.post("/api/auth/discord/callback", json={
            "code": "auth_code_123",
            "state": state,
        })

    # THEN
    assert response.status_code == 200
    assert "access_token" in response.json()

    settings.DISCORD_CLIENT_ID = original_id
    settings.DISCORD_CLIENT_SECRET = original_secret


@pytest.mark.asyncio
async def test_discord_callback_rejects_unverified_email(client: AsyncClient):
    # GIVEN
    state = "test-state-unverified"
    discord_oauth_states[state] = True

    original_id = settings.DISCORD_CLIENT_ID
    original_secret = settings.DISCORD_CLIENT_SECRET
    settings.DISCORD_CLIENT_ID = "test-client-id"
    settings.DISCORD_CLIENT_SECRET = "test-secret"

    unverified_user = {**DISCORD_USER_RESPONSE, "verified": False}

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=_mock_httpx_post())
    mock_client.get = AsyncMock(return_value=_mock_httpx_get(user_data=unverified_user))

    # WHEN
    with patch("app.api.auth.httpx.AsyncClient", return_value=mock_client):
        response = await client.post("/api/auth/discord/callback", json={
            "code": "auth_code_123",
            "state": state,
        })

    # THEN
    assert response.status_code == 400
    assert "vérifié" in response.json()["detail"]

    settings.DISCORD_CLIENT_ID = original_id
    settings.DISCORD_CLIENT_SECRET = original_secret


@pytest.mark.asyncio
async def test_login_rejects_user_without_password(client: AsyncClient, db_session: AsyncSession):
    # GIVEN - user created via Discord SSO (no password)
    user = UserFactory(email="discord_only@veaf.org", nickname="DiscordOnly", password=None, discord_id="999888777")
    db_session.add(user)
    await db_session.flush()

    # WHEN
    response = await client.post("/api/auth/login", json={
        "email": "discord_only@veaf.org",
        "password": "any_password",
    })

    # THEN
    assert response.status_code == 401
