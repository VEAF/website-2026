"""Integration tests for public URL redirect endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UrlFactory


async def _create_url(db: AsyncSession, **overrides):
    """Create and return a URL."""
    url = UrlFactory.build(**overrides)
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


# =============================================================================
# Get URL by slug — GET /api/urls/{slug}
# =============================================================================


@pytest.mark.asyncio
async def test_get_url_by_slug_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    url = await _create_url(db_session, slug="discord", target="https://discord.com/invite/abc")

    # WHEN
    response = await client.get("/api/urls/discord")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "discord"
    assert data["target"] == "https://discord.com/invite/abc"
    assert data["delay"] == 0
    assert data["status"] is True


@pytest.mark.asyncio
async def test_get_url_by_slug_not_found(client: AsyncClient):
    # GIVEN - no URLs in database

    # WHEN
    response = await client.get("/api/urls/nonexistent")

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_url_by_slug_disabled(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    await _create_url(db_session, slug="disabled", target="https://example.com", status=False)

    # WHEN
    response = await client.get("/api/urls/disabled")

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_url_by_slug_includes_delay(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    await _create_url(db_session, slug="teamspeak", target="ts3server://ts.veaf.org", delay=5)

    # WHEN
    response = await client.get("/api/urls/teamspeak")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["delay"] == 5
