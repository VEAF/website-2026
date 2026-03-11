from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.utils.cache import discord_voice_cache


@pytest.fixture(autouse=True)
def clear_discord_voice_cache():
    discord_voice_cache.clear()
    yield
    discord_voice_cache.clear()


@pytest.mark.asyncio
async def test_discord_voice_status_returns_cached_data(client: AsyncClient):
    # GIVEN
    discord_voice_cache["discord_voice_status"] = {
        "users": [
            {"user_id": "111", "nickname": "Pilot1"},
            {"user_id": "222", "nickname": "Pilot2"},
        ],
        "channels": [
            {"channel_id": "10", "name": "Lobby", "users": [{"user_id": "111", "nickname": "Pilot1"}]},
            {"channel_id": "20", "name": "Ops Room", "users": [{"user_id": "222", "nickname": "Pilot2"}]},
        ],
        "user_count": 2,
        "guild_name": "VEAF",
    }

    # WHEN
    with patch("app.api.discord_voice.settings") as mock_settings:
        mock_settings.DISCORD_BOT_TOKEN = "fake-token"
        mock_settings.DISCORD_GUILD_ID = "123456"
        response = await client.get("/api/discord-voice/status")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is True
    assert data["user_count"] == 2
    assert len(data["channels"]) == 2
    assert data["channels"][0]["name"] == "Lobby"
    assert len(data["channels"][0]["users"]) == 1
    assert data["guild_name"] == "VEAF"


@pytest.mark.asyncio
async def test_discord_voice_status_returns_empty_when_not_configured(client: AsyncClient):
    # GIVEN — empty DISCORD_BOT_TOKEN/DISCORD_GUILD_ID

    # WHEN
    with patch("app.api.discord_voice.settings") as mock_settings:
        mock_settings.DISCORD_BOT_TOKEN = ""
        mock_settings.DISCORD_GUILD_ID = ""
        response = await client.get("/api/discord-voice/status")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is False
    assert data["user_count"] == 0
    assert data["users"] == []
    assert data["channels"] == []


@pytest.mark.asyncio
async def test_discord_voice_status_returns_empty_when_cache_empty(client: AsyncClient):
    # GIVEN — configured but cache is empty

    # WHEN
    with patch("app.api.discord_voice.settings") as mock_settings:
        mock_settings.DISCORD_BOT_TOKEN = "fake-token"
        mock_settings.DISCORD_GUILD_ID = "123456"
        response = await client.get("/api/discord-voice/status")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is True
    assert data["user_count"] == 0
    assert data["users"] == []
    assert data["channels"] == []


@pytest.mark.asyncio
async def test_header_includes_discord_voice_count(client: AsyncClient):
    # GIVEN
    discord_voice_cache["discord_voice_status"] = {
        "users": [{"user_id": "111", "nickname": "Pilot1"}],
        "channels": [],
        "user_count": 1,
        "guild_name": "VEAF",
    }

    # WHEN
    response = await client.get("/api/header")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["discord_voice_count"] == 1


@pytest.mark.asyncio
async def test_header_discord_voice_count_zero_when_no_cache(client: AsyncClient):
    # GIVEN — empty cache

    # WHEN
    response = await client.get("/api/header")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["discord_voice_count"] == 0
