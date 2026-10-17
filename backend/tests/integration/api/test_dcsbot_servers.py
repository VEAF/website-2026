"""Integration tests for the public DCSServerBot servers endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import ServerFactory

BOT_SERVER = {"name": "VEAF - Private Foothold 2", "status": "Running", "players": [], "mission": None}
OTHER_SERVER = {"name": "VEAF - Public 1", "status": "Running", "players": [], "mission": None}


@pytest.fixture
def bot():
    with (
        patch("app.services.dcsbot.get_servers", new=AsyncMock(return_value=[BOT_SERVER, OTHER_SERVER])),
        patch("app.services.dcsbot.get_server_stats", new=AsyncMock(return_value=None)),
        patch("app.services.dcsbot.get_server", new=AsyncMock(return_value=[BOT_SERVER])),
        patch("app.services.dcsbot.get_server_stats_by_name", new=AsyncMock(return_value=None)),
        patch("app.services.dcsbot.get_server_attendance", new=AsyncMock(return_value=None)),
    ):
        yield


async def _create_sitac_server(db: AsyncSession):
    server = ServerFactory.build(dcsbot_name=BOT_SERVER["name"], sitac_url="http://dcs.example.org:8080")
    db.add(server)
    await db.commit()


@pytest.mark.asyncio
async def test_servers_list_exposes_sitac_url(client: AsyncClient, db_session: AsyncSession, bot):
    # GIVEN
    await _create_sitac_server(db_session)

    # WHEN
    response = await client.get("/api/dcsbot/servers")

    # THEN
    assert response.status_code == 200
    by_name = {s["name"]: s for s in response.json()["servers"]}
    assert by_name[BOT_SERVER["name"]]["sitac_url"] == "http://dcs.example.org:8080"
    assert by_name[OTHER_SERVER["name"]]["sitac_url"] is None


@pytest.mark.asyncio
async def test_server_detail_exposes_sitac_url_to_anonymous(client: AsyncClient, db_session: AsyncSession, bot):
    # GIVEN
    await _create_sitac_server(db_session)

    # WHEN
    response = await client.get(f"/api/dcsbot/servers/{BOT_SERVER['name']}")

    # THEN
    assert response.status_code == 200
    assert response.json()["server"]["sitac_url"] == "http://dcs.example.org:8080"
