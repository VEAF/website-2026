"""Integration tests for admin URL CRUD endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.content import Url
from tests.factories import AdminFactory, UrlFactory, UserFactory


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


async def _create_url(db: AsyncSession, **overrides) -> Url:
    """Create and return a URL."""
    url = UrlFactory.build(**overrides)
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


# =============================================================================
# List URLs — GET /api/admin/urls
# =============================================================================


@pytest.mark.asyncio
async def test_list_urls_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_url(db_session, slug="alpha")
    await _create_url(db_session, slug="bravo")

    # WHEN
    response = await client.get("/api/admin/urls", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_urls_search(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_url(db_session, slug="discord", target="https://discord.com")
    await _create_url(db_session, slug="facebook", target="https://facebook.com")

    # WHEN
    response = await client.get("/api/admin/urls", params={"search": "discord"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "discord"


@pytest.mark.asyncio
async def test_list_urls_filter_status(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_url(db_session, slug="active", status=True)
    await _create_url(db_session, slug="inactive", status=False)

    # WHEN
    response = await client.get("/api/admin/urls", params={"status": "true"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "active"


@pytest.mark.asyncio
async def test_list_urls_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    for i in range(5):
        await _create_url(db_session, slug=f"url-p-{i}")

    # WHEN
    response = await client.get("/api/admin/urls", params={"skip": 2, "limit": 2}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_urls_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.get("/api/admin/urls")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_urls_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/urls", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Create URL — POST /api/admin/urls
# =============================================================================


@pytest.mark.asyncio
async def test_create_url_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/urls", json={
        "slug": "discord",
        "target": "https://discord.com/invite/abc",
        "delay": 5,
        "status": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "discord"
    assert data["target"] == "https://discord.com/invite/abc"
    assert data["delay"] == 5
    assert data["status"] is True
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_url_defaults(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/urls", json={
        "slug": "test",
        "target": "https://example.com",
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["delay"] == 0
    assert data["status"] is True


@pytest.mark.asyncio
async def test_create_url_duplicate_slug(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_url(db_session, slug="existing")

    # WHEN
    response = await client.post("/api/admin/urls", json={
        "slug": "existing",
        "target": "https://other.com",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_url_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.post("/api/admin/urls", json={
        "slug": "nope",
        "target": "https://example.com",
    })

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_url_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/urls", json={
        "slug": "nope",
        "target": "https://example.com",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get URL — GET /api/admin/urls/{url_id}
# =============================================================================


@pytest.mark.asyncio
async def test_get_url_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    url = await _create_url(db_session, slug="detail", delay=3)

    # WHEN
    response = await client.get(f"/api/admin/urls/{url.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == url.id
    assert data["slug"] == "detail"
    assert data["delay"] == 3


@pytest.mark.asyncio
async def test_get_url_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/urls/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Update URL — PUT /api/admin/urls/{url_id}
# =============================================================================


@pytest.mark.asyncio
async def test_update_url_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    url = await _create_url(db_session, slug="old", target="https://old.com", delay=0)

    # WHEN
    response = await client.put(f"/api/admin/urls/{url.id}", json={
        "slug": "new",
        "target": "https://new.com",
        "delay": 10,
        "status": False,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "new"
    assert data["target"] == "https://new.com"
    assert data["delay"] == 10
    assert data["status"] is False


@pytest.mark.asyncio
async def test_update_url_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/urls/9999", json={
        "slug": "nope",
        "target": "https://example.com",
        "delay": 0,
        "status": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_url_duplicate_slug(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_url(db_session, slug="taken")
    url = await _create_url(db_session, slug="mine")

    # WHEN
    response = await client.put(f"/api/admin/urls/{url.id}", json={
        "slug": "taken",
        "target": url.target,
        "delay": 0,
        "status": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


# =============================================================================
# Delete URL — DELETE /api/admin/urls/{url_id}
# =============================================================================


@pytest.mark.asyncio
async def test_delete_url_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    url = await _create_url(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/urls/{url.id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify deletion
    deleted = await db_session.get(Url, url.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_url_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/urls/9999", headers=headers)

    # THEN
    assert response.status_code == 404
