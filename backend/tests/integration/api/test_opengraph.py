"""Integration tests for the Open Graph meta tags endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.calendar import CalendarEvent
from app.models.content import Page, PageBlock
from tests.factories import EventFactory, FileFactory, PageBlockFactory, PageFactory, UserFactory


async def _create_user(db: AsyncSession):
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_event(db: AsyncSession, owner_id: int, **kwargs) -> CalendarEvent:
    event = EventFactory.build(owner_id=owner_id, **kwargs)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def _create_page(db: AsyncSession, **kwargs) -> Page:
    page = PageFactory.build(**kwargs)
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


async def _create_page_block(db: AsyncSession, page_id: int, **kwargs) -> PageBlock:
    block = PageBlockFactory.build(page_id=page_id, **kwargs)
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block


@pytest.mark.asyncio
async def test_og_default_returns_fallback_tags(client: AsyncClient):
    # WHEN
    response = await client.get("/api/og", params={"path": "/"})

    # THEN
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert 'og:title" content="VEAF - Virtual European Air Force"' in body
    assert 'og:description" content="Site communautaire de la Virtual European Air Force' in body
    base_url = settings.APP_URL.rstrip("/")
    assert f'og:image" content="{base_url}/img/Logo_veaf.webp"' in body
    assert 'og:site_name" content="VEAF - Virtual European Air Force"' in body


@pytest.mark.asyncio
async def test_og_calendar_event_returns_event_tags(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    event = await _create_event(db_session, owner_id=user.id, title="Mission Alpha", description="Briefing at 20h")

    # WHEN
    response = await client.get("/api/og", params={"path": f"/calendar/{event.id}"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert "Mission Alpha - VEAF" in body
    assert "Briefing at 20h" in body
    assert 'og:type" content="article"' in body


@pytest.mark.asyncio
async def test_og_calendar_event_with_image(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    file = FileFactory.build()
    db_session.add(file)
    await db_session.commit()
    await db_session.refresh(file)
    event = await _create_event(db_session, owner_id=user.id, title="OPEX Bravo", image_id=file.id)

    # WHEN
    response = await client.get("/api/og", params={"path": f"/calendar/{event.id}"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert f"/api/files/{file.uuid}" in body


@pytest.mark.asyncio
async def test_og_calendar_event_not_found_returns_defaults(client: AsyncClient):
    # WHEN
    response = await client.get("/api/og", params={"path": "/calendar/99999"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert 'og:title" content="VEAF - Virtual European Air Force"' in body


@pytest.mark.asyncio
async def test_og_calendar_deleted_event_returns_defaults(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    event = await _create_event(db_session, owner_id=user.id, title="Deleted Event", deleted=True)

    # WHEN
    response = await client.get("/api/og", params={"path": f"/calendar/{event.id}"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert "Deleted Event" not in body
    assert 'og:title" content="VEAF - Virtual European Air Force"' in body


@pytest.mark.asyncio
async def test_og_cms_page_returns_page_tags(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    page = await _create_page(db_session, title="Charte du pilote", path="charte-du-pilote")
    await _create_page_block(db_session, page_id=page.id, content="Bienvenue dans la VEAF. Voici notre charte.")

    # WHEN
    response = await client.get("/api/og", params={"path": "/charte-du-pilote"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert "Charte du pilote - VEAF" in body
    assert "Bienvenue dans la VEAF" in body


@pytest.mark.asyncio
async def test_og_cms_page_disabled_returns_defaults(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    await _create_page(db_session, title="Draft Page", path="draft-page", enabled=False)

    # WHEN
    response = await client.get("/api/og", params={"path": "/draft-page"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert "Draft Page" not in body


@pytest.mark.asyncio
async def test_og_unknown_path_returns_defaults(client: AsyncClient):
    # WHEN
    response = await client.get("/api/og", params={"path": "/login"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert 'og:title" content="VEAF - Virtual European Air Force"' in body


@pytest.mark.asyncio
async def test_og_html_escapes_content(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — title with special HTML characters
    user = await _create_user(db_session)
    event = await _create_event(db_session, owner_id=user.id, title='Test <script>alert("xss")</script>', description="Safe desc")

    # WHEN
    response = await client.get("/api/og", params={"path": f"/calendar/{event.id}"})

    # THEN
    assert response.status_code == 200
    body = response.text
    assert "<script>" not in body
    assert "&lt;script&gt;" in body
