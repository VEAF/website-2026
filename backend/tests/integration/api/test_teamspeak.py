import pytest
from httpx import AsyncClient

from app.utils.cache import teamspeak_cache


@pytest.fixture(autouse=True)
def clear_ts_cache():
    teamspeak_cache.clear()
    yield
    teamspeak_cache.clear()


@pytest.mark.asyncio
async def test_teamspeak_status_returns_cached_data(client: AsyncClient):
    # GIVEN
    teamspeak_cache["ts_status"] = {
        "clients": [
            {"clid": 1, "cid": 10, "nickname": "Pilot1"},
            {"clid": 2, "cid": 20, "nickname": "Pilot2"},
        ],
        "channels": [
            {"cid": 10, "pid": 0, "name": "Lobby", "clients": [{"clid": 1, "cid": 10, "nickname": "Pilot1"}]},
            {"cid": 20, "pid": 0, "name": "Ops Room", "clients": [{"clid": 2, "cid": 20, "nickname": "Pilot2"}]},
        ],
        "client_count": 2,
    }

    # WHEN
    response = await client.get("/api/teamspeak/status")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is True
    assert data["client_count"] == 2
    assert len(data["channels"]) == 2
    assert data["channels"][0]["name"] == "Lobby"
    assert len(data["channels"][0]["clients"]) == 1
    assert data["server_host"] != ""


@pytest.mark.asyncio
async def test_teamspeak_status_returns_empty_when_cache_empty(client: AsyncClient):
    # GIVEN — cache is empty but TS is configured

    # WHEN
    response = await client.get("/api/teamspeak/status")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is True
    assert data["client_count"] == 0
    assert data["clients"] == []
    assert data["channels"] == []


@pytest.mark.asyncio
async def test_header_includes_ts_client_count(client: AsyncClient):
    # GIVEN
    teamspeak_cache["ts_status"] = {
        "clients": [{"clid": 1, "cid": 10, "nickname": "Pilot1"}],
        "channels": [],
        "client_count": 1,
    }

    # WHEN
    response = await client.get("/api/header")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["ts_client_count"] == 1


@pytest.mark.asyncio
async def test_header_ts_client_count_zero_when_no_cache(client: AsyncClient):
    # GIVEN — empty cache

    # WHEN
    response = await client.get("/api/header")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["ts_client_count"] == 0
