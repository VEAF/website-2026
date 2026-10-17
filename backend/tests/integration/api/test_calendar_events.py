"""Integration tests for public calendar events endpoint."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.calendar import CalendarEvent
from app.models.content import File
from app.models.module import Module
from app.models.user import User
from tests.factories import EventFactory, FileFactory, ModuleFactory, UserFactory


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


async def _create_file(db: AsyncSession) -> File:
    """Create an image File and return it."""
    file = FileFactory.build()
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def _create_map(db: AsyncSession, image_header_id: int | None = None) -> Module:
    """Create a map module, optionally with a header image."""
    module = ModuleFactory.build(type=Module.TYPE_MAP, image_header_id=image_header_id)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


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
async def test_get_event_deleted_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    event = await _create_event(
        db_session, owner_id=user.id, title="Deleted", deleted=True,
        start_date=datetime(2026, 2, 11, 20, 0), end_date=datetime(2026, 2, 11, 23, 0),
    )

    # WHEN
    response = await client.get(f"/api/calendar/events/{event.id}")

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_member_restricted_stays_public(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    event = await _create_event(
        db_session, owner_id=user.id, title="Members only", restrictions=str(CalendarEvent.RESTRICTION_MEMBER),
        start_date=datetime(2026, 2, 12, 20, 0), end_date=datetime(2026, 2, 12, 23, 0),
    )

    # WHEN
    response = await client.get(f"/api/calendar/events/{event.id}")

    # THEN
    assert response.status_code == 200
    assert response.json()["title"] == "Members only"


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


@pytest.mark.asyncio
async def test_list_events_invalid_date_returns_422(client: AsyncClient):
    # WHEN
    response = await client.get("/api/calendar/events?from_date=not-a-date")

    # THEN
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_event_exposes_map_image_header_uuid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN an event without its own image, linked to a map having a header image
    user = await _create_user(db_session)
    image_header = await _create_file(db_session)
    map_module = await _create_map(db_session, image_header_id=image_header.id)
    event = await _create_event(db_session, owner_id=user.id, map_id=map_module.id, image_id=None)

    # WHEN
    response = await client.get(f"/api/calendar/events/{event.id}")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["image_uuid"] is None
    assert data["map_image_header_uuid"] == image_header.uuid


@pytest.mark.asyncio
async def test_get_event_map_without_image_header(client: AsyncClient, db_session: AsyncSession):
    # GIVEN an event linked to a map that has no header image
    user = await _create_user(db_session)
    map_module = await _create_map(db_session)
    event = await _create_event(db_session, owner_id=user.id, map_id=map_module.id, image_id=None)

    # WHEN
    response = await client.get(f"/api/calendar/events/{event.id}")

    # THEN
    assert response.status_code == 200
    assert response.json()["map_image_header_uuid"] is None


@pytest.mark.asyncio
async def test_get_event_without_map(client: AsyncClient, db_session: AsyncSession):
    # GIVEN an event with neither map nor image
    user = await _create_user(db_session)
    event = await _create_event(db_session, owner_id=user.id, map_id=None, image_id=None)

    # WHEN
    response = await client.get(f"/api/calendar/events/{event.id}")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["map_image_header_uuid"] is None
    assert data["image_uuid"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("status,expected", [(User.STATUS_CADET, 200), (User.STATUS_MEMBER, 200), (User.STATUS_UNKNOWN, 403)])
async def test_vote_event_open_to_cadets_and_members(
    client: AsyncClient, db_session: AsyncSession, status: int, expected: int
):
    # GIVEN
    owner = await _create_user(db_session)
    voter = UserFactory.build(status=status, sim_dcs=True)
    db_session.add(voter)
    await db_session.commit()
    await db_session.refresh(voter)
    headers = {"Authorization": f"Bearer {create_access_token(voter.id, voter.get_roles_list())}"}
    start = datetime.now(UTC) + timedelta(days=2)
    # Not refreshed: SQLite would hand the dates back without their time zone
    event = EventFactory.build(
        owner_id=owner.id, registration=True, sim_dcs=True, sim_bms=False,
        restrictions=f"{CalendarEvent.RESTRICTION_CADET},{CalendarEvent.RESTRICTION_MEMBER}",
        start_date=start, end_date=start + timedelta(hours=3),
    )
    db_session.add(event)
    await db_session.commit()

    # WHEN
    response = await client.post(f"/api/calendar/events/{event.id}/vote", json={"vote": True}, headers=headers)

    # THEN
    assert response.status_code == expected


@pytest.mark.asyncio
async def test_copy_event_keeps_image(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    owner = await _create_user(db_session)
    headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.get_roles_list())}"}
    image = await _create_file(db_session)
    event = await _create_event(
        db_session, owner_id=owner.id, title="Illustrated", image_id=image.id,
        start_date=datetime(2026, 3, 1, 20, 0), end_date=datetime(2026, 3, 1, 23, 0),
    )

    # WHEN
    response = await client.post(f"/api/calendar/events/{event.id}/copy", headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != event.id
    assert data["title"] == "Illustrated"
    assert data["image_uuid"] == image.uuid
