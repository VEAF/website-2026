"""Integration tests for admin event endpoints."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.calendar import CalendarEvent
from app.models.user import User
from tests.factories import AdminFactory, EventFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession, **kwargs) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_event(db: AsyncSession, owner_id: int, **kwargs) -> CalendarEvent:
    """Create a CalendarEvent and return it."""
    event = EventFactory.build(owner_id=owner_id, **kwargs)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


# =============================================================================
# List events
# =============================================================================


@pytest.mark.asyncio
async def test_list_events_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_event(db_session, owner_id=admin.id, title="Alpha Training")
    await _create_event(db_session, owner_id=admin.id, title="Bravo Mission")

    # WHEN
    response = await client.get("/api/admin/events", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 2
    item = data["items"][0]
    assert "title" in item
    assert "type_as_string" in item
    assert "deleted" in item
    assert "owner_nickname" in item


@pytest.mark.asyncio
async def test_list_events_search_by_title(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_event(db_session, owner_id=admin.id, title="OPEX Bosphore")
    await _create_event(db_session, owner_id=admin.id, title="Training Caucase")

    # WHEN
    response = await client.get("/api/admin/events?search=bosphore", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "OPEX Bosphore"


@pytest.mark.asyncio
async def test_list_events_filter_by_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_event(db_session, owner_id=admin.id, type=CalendarEvent.EVENT_TYPE_TRAINING)
    await _create_event(db_session, owner_id=admin.id, type=CalendarEvent.EVENT_TYPE_MISSION)

    # WHEN
    response = await client.get(f"/api/admin/events?type={CalendarEvent.EVENT_TYPE_MISSION}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == CalendarEvent.EVENT_TYPE_MISSION


@pytest.mark.asyncio
async def test_list_events_filter_by_deleted(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_event(db_session, owner_id=admin.id, deleted=False)
    await _create_event(db_session, owner_id=admin.id, deleted=True)

    # WHEN — only deleted
    response = await client.get("/api/admin/events?deleted=true", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["deleted"] is True

    # WHEN — only active
    response = await client.get("/api/admin/events?deleted=false", headers=headers)

    # THEN
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["deleted"] is False


@pytest.mark.asyncio
async def test_list_events_filter_by_sim(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_event(db_session, owner_id=admin.id, sim_dcs=True, sim_bms=False)
    await _create_event(db_session, owner_id=admin.id, sim_dcs=False, sim_bms=True)

    # WHEN
    response = await client.get("/api/admin/events?sim=bms", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sim_bms"] is True


@pytest.mark.asyncio
async def test_list_events_filter_by_date_range(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    now = datetime.now(UTC)
    await _create_event(db_session, owner_id=admin.id, title="Past", start_date=now - timedelta(days=30), end_date=now - timedelta(days=29))
    await _create_event(db_session, owner_id=admin.id, title="Future", start_date=now + timedelta(days=10), end_date=now + timedelta(days=11))

    # WHEN — filter from tomorrow onward
    date_from = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    response = await client.get(f"/api/admin/events?date_from={date_from}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Future"

    # WHEN — filter up to yesterday
    date_to = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    response = await client.get(f"/api/admin/events?date_to={date_to}", headers=headers)

    # THEN
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Past"


@pytest.mark.asyncio
async def test_list_events_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    for i in range(5):
        await _create_event(db_session, owner_id=admin.id)

    # WHEN
    response = await client.get("/api/admin/events?skip=2&limit=2", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_events_default_order_desc(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    now = datetime.now(UTC)
    await _create_event(db_session, owner_id=admin.id, title="Old", start_date=now - timedelta(days=10), end_date=now - timedelta(days=9))
    await _create_event(db_session, owner_id=admin.id, title="Recent", start_date=now + timedelta(days=1), end_date=now + timedelta(days=2))

    # WHEN
    response = await client.get("/api/admin/events", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["title"] == "Recent"
    assert data["items"][1]["title"] == "Old"


@pytest.mark.asyncio
async def test_list_events_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.get("/api/admin/events")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_events_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/events", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get event detail
# =============================================================================


@pytest.mark.asyncio
async def test_get_event_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    event = await _create_event(db_session, owner_id=admin.id, title="Detail Test")

    # WHEN
    response = await client.get(f"/api/admin/events/{event.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event.id
    assert data["title"] == "Detail Test"
    assert "votes" in data
    assert "choices" in data
    assert "flights" in data


@pytest.mark.asyncio
async def test_get_event_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/events/9999", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/events/1", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Restore event
# =============================================================================


@pytest.mark.asyncio
async def test_restore_event_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    event = await _create_event(
        db_session, owner_id=admin.id, deleted=True, deleted_at=datetime.now(UTC)
    )

    # WHEN
    response = await client.patch(f"/api/admin/events/{event.id}/restore", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is False
    assert data["deleted_at"] is None


@pytest.mark.asyncio
async def test_restore_event_not_deleted(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    event = await _create_event(db_session, owner_id=admin.id, deleted=False)

    # WHEN
    response = await client.patch(f"/api/admin/events/{event.id}/restore", headers=headers)

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_restore_event_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.patch("/api/admin/events/9999/restore", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_restore_event_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.patch("/api/admin/events/1/restore", headers=headers)

    # THEN
    assert response.status_code == 403
