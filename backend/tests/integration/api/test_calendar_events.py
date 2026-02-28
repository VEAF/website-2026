"""Integration tests for public calendar events endpoint."""

from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar import CalendarEvent
from tests.factories import EventFactory, UserFactory


async def _create_user(db: AsyncSession):
    """Create a user and return it."""
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_event(db: AsyncSession, owner_id: int, **kwargs) -> CalendarEvent:
    """Create a CalendarEvent and return it."""
    event = EventFactory.build(owner_id=owner_id, **kwargs)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@pytest.mark.asyncio
async def test_list_events_no_filters(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    await _create_event(db_session, owner_id=user.id, title="Alpha")
    await _create_event(db_session, owner_id=user.id, title="Bravo")

    # WHEN
    response = await client.get("/api/calendar/events")

    # THEN
    assert response.status_code == 200
    data = response.json()
    titles = [e["title"] for e in data]
    assert "Alpha" in titles
    assert "Bravo" in titles


@pytest.mark.asyncio
async def test_list_events_with_date_range(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — Feb 2026 month view shows Jan 26 to Mar 9 (exclusive)
    user = await _create_user(db_session)
    await _create_event(
        db_session, owner_id=user.id, title="Jan Event",
        start_date=datetime(2026, 1, 27, 20, 0), end_date=datetime(2026, 1, 27, 23, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Feb Event",
        start_date=datetime(2026, 2, 10, 20, 0), end_date=datetime(2026, 2, 10, 23, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Mar Event",
        start_date=datetime(2026, 3, 7, 20, 0), end_date=datetime(2026, 3, 7, 23, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Dec Event",
        start_date=datetime(2025, 12, 15, 20, 0), end_date=datetime(2025, 12, 15, 23, 0),
    )

    # WHEN
    response = await client.get("/api/calendar/events?from_date=2026-01-26&to_date=2026-03-09")

    # THEN
    assert response.status_code == 200
    data = response.json()
    titles = [e["title"] for e in data]
    assert "Jan Event" in titles
    assert "Feb Event" in titles
    assert "Mar Event" in titles
    assert "Dec Event" not in titles


@pytest.mark.asyncio
async def test_list_events_excludes_deleted(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    await _create_event(
        db_session, owner_id=user.id, title="Active",
        start_date=datetime(2026, 2, 10, 20, 0), end_date=datetime(2026, 2, 10, 23, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Deleted", deleted=True,
        start_date=datetime(2026, 2, 11, 20, 0), end_date=datetime(2026, 2, 11, 23, 0),
    )

    # WHEN
    response = await client.get("/api/calendar/events?from_date=2026-02-01&to_date=2026-02-28")

    # THEN
    assert response.status_code == 200
    data = response.json()
    titles = [e["title"] for e in data]
    assert "Active" in titles
    assert "Deleted" not in titles


@pytest.mark.asyncio
async def test_list_events_from_date_only(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    await _create_event(
        db_session, owner_id=user.id, title="Old",
        start_date=datetime(2025, 6, 1, 10, 0), end_date=datetime(2025, 6, 1, 12, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Recent",
        start_date=datetime(2026, 2, 10, 20, 0), end_date=datetime(2026, 2, 10, 23, 0),
    )

    # WHEN
    response = await client.get("/api/calendar/events?from_date=2026-01-01")

    # THEN
    assert response.status_code == 200
    data = response.json()
    titles = [e["title"] for e in data]
    assert "Recent" in titles
    assert "Old" not in titles


@pytest.mark.asyncio
async def test_list_events_to_date_only(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    await _create_event(
        db_session, owner_id=user.id, title="Early",
        start_date=datetime(2026, 1, 5, 10, 0), end_date=datetime(2026, 1, 5, 12, 0),
    )
    await _create_event(
        db_session, owner_id=user.id, title="Late",
        start_date=datetime(2026, 12, 20, 20, 0), end_date=datetime(2026, 12, 20, 23, 0),
    )

    # WHEN
    response = await client.get("/api/calendar/events?to_date=2026-02-01")

    # THEN
    assert response.status_code == 200
    data = response.json()
    titles = [e["title"] for e in data]
    assert "Early" in titles
    assert "Late" not in titles
