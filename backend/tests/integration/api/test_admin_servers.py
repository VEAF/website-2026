"""Integration tests for admin server CRUD endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.dcs import Server
from tests.factories import AdminFactory, ServerFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_server(db: AsyncSession, **overrides) -> Server:
    """Create and return a server."""
    server = ServerFactory.build(**overrides)
    db.add(server)
    await db.commit()
    await db.refresh(server)
    return server


# =============================================================================
# List servers — GET /api/admin/servers
# =============================================================================


@pytest.mark.asyncio
async def test_list_servers_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_server(db_session, name="Alpha")
    await _create_server(db_session, name="Bravo")

    # WHEN
    response = await client.get("/api/admin/servers", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_servers_search_by_name(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_server(db_session, name="Combat Server", code="combat")
    await _create_server(db_session, name="Training Server", code="training")

    # WHEN
    response = await client.get("/api/admin/servers", params={"search": "combat"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Combat Server"


@pytest.mark.asyncio
async def test_list_servers_search_by_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_server(db_session, name="Server A", code="srv-main")
    await _create_server(db_session, name="Server B", code="srv-test")

    # WHEN
    response = await client.get("/api/admin/servers", params={"search": "main"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["code"] == "srv-main"


@pytest.mark.asyncio
async def test_list_servers_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    for i in range(5):
        await _create_server(db_session, name=f"Server {i}", code=f"srv-{i}")

    # WHEN
    response = await client.get("/api/admin/servers", params={"skip": 2, "limit": 2}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_servers_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.get("/api/admin/servers")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_servers_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/servers", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Create server — POST /api/admin/servers
# =============================================================================


@pytest.mark.asyncio
async def test_create_server_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/servers", json={
        "name": "Combat Server",
        "code": "combat",
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Combat Server"
    assert data["code"] == "combat"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_server_defaults(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/servers", json={
        "name": "Test Server",
        "code": "test",
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Server"
    assert data["code"] == "test"


@pytest.mark.asyncio
async def test_create_server_duplicate_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_server(db_session, code="existing")

    # WHEN
    response = await client.post("/api/admin/servers", json={
        "name": "Another Server",
        "code": "existing",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_server_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.post("/api/admin/servers", json={
        "name": "Nope",
        "code": "nope",
    })

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_server_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/servers", json={
        "name": "Nope",
        "code": "nope",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get server — GET /api/admin/servers/{server_id}
# =============================================================================


@pytest.mark.asyncio
async def test_get_server_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    server = await _create_server(db_session, name="Detail Server", code="detail")

    # WHEN
    response = await client.get(f"/api/admin/servers/{server.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == server.id
    assert data["name"] == "Detail Server"
    assert data["code"] == "detail"


@pytest.mark.asyncio
async def test_get_server_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/servers/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Update server — PUT /api/admin/servers/{server_id}
# =============================================================================


@pytest.mark.asyncio
async def test_update_server_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    server = await _create_server(db_session, name="Old Name", code="old")

    # WHEN
    response = await client.put(f"/api/admin/servers/{server.id}", json={
        "name": "New Name",
        "code": "new",
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["code"] == "new"


@pytest.mark.asyncio
async def test_update_server_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/servers/9999", json={
        "name": "Nope",
        "code": "nope",
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_server_duplicate_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_server(db_session, code="taken")
    server = await _create_server(db_session, code="mine")

    # WHEN
    response = await client.put(f"/api/admin/servers/{server.id}", json={
        "name": server.name,
        "code": "taken",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


# =============================================================================
# Delete server — DELETE /api/admin/servers/{server_id}
# =============================================================================


@pytest.mark.asyncio
async def test_delete_server_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    server = await _create_server(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/servers/{server.id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify deletion
    deleted = await db_session.get(Server, server.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_server_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/servers/9999", headers=headers)

    # THEN
    assert response.status_code == 404
