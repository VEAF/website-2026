"""Integration tests for the public DCS statistics of a user profile."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import PlayerFactory, UserFactory

BOT_STATS = {
    "playtime": 7200,
    "kills": 12,
    "deaths": 3,
    "kdr": 4.0,
    "takeoffs": 9,
    "landings": 8,
    "killsByModule": [{"module": "F-16C_50", "kills": 10}, {"module": "AH-64D_BLK_II", "kills": 2}],
}


async def _create_user(db: AsyncSession, with_player: bool = True):
    player = None
    if with_player:
        player = PlayerFactory.build(ucid="u-1", nickname="Viper")
        db.add(player)
        await db.flush()
    user = UserFactory.build(nickname="ViperVEAF", discord_id="42", player_id=player.id if player else None)
    db.add(user)
    await db.commit()
    return user


@pytest.mark.asyncio
async def test_dcs_stats_public_and_mapped(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    fetch = AsyncMock(return_value=BOT_STATS)

    # WHEN
    with patch("app.services.dcsbot.get_player_stats", new=fetch):
        response = await client.get(f"/api/users/{user.id}/dcs-stats")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["has_player"] is True
    assert data["stats"]["playtime"] == 7200
    assert data["stats"]["kills"] == 12
    assert data["stats"]["kills_pvp"] == 0
    assert data["stats"]["kills_by_module"] == [
        {"module": "F-16C_50", "kills": 10},
        {"module": "AH-64D_BLK_II", "kills": 2},
    ]
    fetch.assert_awaited_once_with("u-1", "42", ("Viper", "ViperVEAF"))


@pytest.mark.asyncio
async def test_dcs_stats_without_player(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session, with_player=False)

    # WHEN
    response = await client.get(f"/api/users/{user.id}/dcs-stats")

    # THEN
    assert response.status_code == 200
    assert response.json()["has_player"] is False


@pytest.mark.asyncio
async def test_dcs_stats_bot_unavailable(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)

    # WHEN
    with patch("app.services.dcsbot.get_player_stats", new=AsyncMock(return_value=None)):
        response = await client.get(f"/api/users/{user.id}/dcs-stats")

    # THEN
    assert response.status_code == 200
    assert response.json() == {"has_player": True, "stats": None}


@pytest.mark.asyncio
async def test_dcs_stats_unknown_user(client: AsyncClient):
    # WHEN
    response = await client.get("/api/users/999999/dcs-stats")

    # THEN
    assert response.status_code == 404
