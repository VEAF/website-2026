"""Integration tests for admin DCS player CRUD endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.dcs import Player
from app.models.user import User
from tests.factories import AdminFactory, PlayerFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession, **overrides) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build(**overrides)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_player(db: AsyncSession, **overrides) -> Player:
    """Create and return a DCS player."""
    player = PlayerFactory.build(**overrides)
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


async def _link(db: AsyncSession, user: User, player: Player) -> None:
    """Link a user to a player (the User side owns the FK)."""
    user.player_id = player.id
    await db.commit()


# =============================================================================
# List players — GET /api/admin/players
# =============================================================================


@pytest.mark.asyncio
async def test_list_players_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, nickname="Alpha")
    await _create_player(db_session, nickname="Bravo")

    # WHEN
    response = await client.get("/api/admin/players", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["nickname"] == "Alpha"


@pytest.mark.asyncio
async def test_list_players_exposes_ucid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, nickname="Maverick", ucid="3f9a1c7e4b8d05612a7f3e9c1d4b8a06")

    # WHEN
    response = await client.get("/api/admin/players", headers=headers)

    # THEN
    assert response.status_code == 200
    assert response.json()["items"][0]["ucid"] == "3f9a1c7e4b8d05612a7f3e9c1d4b8a06"


@pytest.mark.asyncio
async def test_list_players_includes_linked_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")
    player = await _create_player(db_session, nickname="Zip_DCS")
    await _link(db_session, pilot, player)
    await _create_player(db_session, nickname="Unlinked")

    # WHEN
    response = await client.get("/api/admin/players", params={"search": "Zip_DCS"}, headers=headers)

    # THEN
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["user_id"] == pilot.id
    assert item["user_nickname"] == "Zip"


@pytest.mark.asyncio
async def test_list_players_unlinked_player_has_no_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, nickname="Solo")

    # WHEN
    response = await client.get("/api/admin/players", headers=headers)

    # THEN
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["user_id"] is None
    assert item["user_nickname"] is None


@pytest.mark.asyncio
async def test_list_players_search_by_ucid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, nickname="Alpha", ucid="aaaa1111bbbb2222cccc3333dddd4444")
    await _create_player(db_session, nickname="Bravo", ucid="99998888777766665555444433332222")

    # WHEN
    response = await client.get("/api/admin/players", params={"search": "bbbb2222"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nickname"] == "Alpha"


@pytest.mark.asyncio
async def test_list_players_search_by_nickname(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, nickname="Maverick")
    await _create_player(db_session, nickname="Goose")

    # WHEN
    response = await client.get("/api/admin/players", params={"search": "maver"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nickname"] == "Maverick"


@pytest.mark.asyncio
async def test_list_players_search_by_user_nickname(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Jarhead")
    player = await _create_player(db_session, nickname="Alpha")
    await _link(db_session, pilot, player)
    await _create_player(db_session, nickname="Bravo")

    # WHEN
    response = await client.get("/api/admin/players", params={"search": "jarhead"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nickname"] == "Alpha"


@pytest.mark.asyncio
async def test_list_players_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    for i in range(5):
        await _create_player(db_session, nickname=f"Pilot {i}")

    # WHEN
    response = await client.get("/api/admin/players", params={"skip": 2, "limit": 2}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_players_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.get("/api/admin/players")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_players_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/players", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Create player — POST /api/admin/players
# =============================================================================


@pytest.mark.asyncio
async def test_create_player_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/players", json={
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
        "nickname": "Maverick",
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["ucid"] == "3f9a1c7e4b8d05612a7f3e9c1d4b8a06"
    assert data["nickname"] == "Maverick"
    assert data["user_id"] is None
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_player_with_user_link(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")

    # WHEN
    response = await client.post("/api/admin/players", json={
        "ucid": "8c2d5f1b9e304a7c6d1f8b2e5a903c74",
        "nickname": "Zip_DCS",
        "user_id": pilot.id,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == pilot.id
    assert data["user_nickname"] == "Zip"
    await db_session.refresh(pilot)
    assert pilot.player_id == data["id"]


@pytest.mark.asyncio
async def test_create_player_duplicate_ucid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, ucid="3f9a1c7e4b8d05612a7f3e9c1d4b8a06")

    # WHEN
    response = await client.post("/api/admin/players", json={
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
        "nickname": "Clone",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_player_unknown_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/players", json={
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
        "nickname": "Maverick",
        "user_id": 99999,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_player_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/players", json={
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get player — GET /api/admin/players/{player_id}
# =============================================================================


@pytest.mark.asyncio
async def test_get_player_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")
    player = await _create_player(db_session, nickname="Zip_DCS")
    await _link(db_session, pilot, player)

    # WHEN
    response = await client.get(f"/api/admin/players/{player.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["ucid"] == player.ucid
    assert data["user_nickname"] == "Zip"


@pytest.mark.asyncio
async def test_get_player_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/players/99999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Update player — PUT /api/admin/players/{player_id}
# =============================================================================


@pytest.mark.asyncio
async def test_update_player_ucid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    player = await _create_player(db_session, ucid="aaaa1111bbbb2222cccc3333dddd4444", nickname="Alpha")

    # WHEN
    response = await client.put(f"/api/admin/players/{player.id}", json={
        "ucid": "99998888777766665555444433332222",
        "nickname": "Alpha",
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    assert response.json()["ucid"] == "99998888777766665555444433332222"
    await db_session.refresh(player)
    assert player.ucid == "99998888777766665555444433332222"


@pytest.mark.asyncio
async def test_update_player_duplicate_ucid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_player(db_session, ucid="aaaa1111bbbb2222cccc3333dddd4444")
    player = await _create_player(db_session, ucid="99998888777766665555444433332222")

    # WHEN
    response = await client.put(f"/api/admin/players/{player.id}", json={
        "ucid": "aaaa1111bbbb2222cccc3333dddd4444",
        "nickname": "Clone",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_player_links_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")
    player = await _create_player(db_session, nickname="Zip_DCS")

    # WHEN
    response = await client.put(f"/api/admin/players/{player.id}", json={
        "ucid": player.ucid,
        "nickname": "Zip_DCS",
        "user_id": pilot.id,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    assert response.json()["user_nickname"] == "Zip"
    await db_session.refresh(pilot)
    assert pilot.player_id == player.id


@pytest.mark.asyncio
async def test_update_player_unlinks_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")
    player = await _create_player(db_session, nickname="Zip_DCS")
    await _link(db_session, pilot, player)

    # WHEN
    response = await client.put(f"/api/admin/players/{player.id}", json={
        "ucid": player.ucid,
        "nickname": "Zip_DCS",
        "user_id": None,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] is None
    assert data["user_nickname"] is None
    await db_session.refresh(pilot)
    assert pilot.player_id is None


@pytest.mark.asyncio
async def test_update_player_moving_link_detaches_previous_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    previous, _ = await _create_user(db_session, nickname="Previous")
    new_owner, _ = await _create_user(db_session, nickname="NewOwner")
    player = await _create_player(db_session, nickname="Shared")
    await _link(db_session, previous, player)

    # WHEN
    response = await client.put(f"/api/admin/players/{player.id}", json={
        "ucid": player.ucid,
        "nickname": "Shared",
        "user_id": new_owner.id,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    assert response.json()["user_nickname"] == "NewOwner"
    await db_session.refresh(previous)
    await db_session.refresh(new_owner)
    assert previous.player_id is None
    assert new_owner.player_id == player.id


@pytest.mark.asyncio
async def test_update_player_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/players/99999", json={
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
    }, headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Delete player — DELETE /api/admin/players/{player_id}
# =============================================================================


@pytest.mark.asyncio
async def test_delete_player_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    player = await _create_player(db_session, nickname="Ghost")

    # WHEN
    response = await client.delete(f"/api/admin/players/{player.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    assert await db_session.get(Player, player.id) is None


@pytest.mark.asyncio
async def test_delete_player_detaches_linked_user(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    pilot, _ = await _create_user(db_session, nickname="Zip")
    player = await _create_player(db_session, nickname="Zip_DCS")
    await _link(db_session, pilot, player)

    # WHEN
    response = await client.delete(f"/api/admin/players/{player.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(pilot)
    assert pilot.player_id is None
    assert await db_session.get(User, pilot.id) is not None


@pytest.mark.asyncio
async def test_delete_player_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/players/99999", headers=headers)

    # THEN
    assert response.status_code == 404
