"""Integration tests for admin recruitment endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.recruitment import RecruitmentEvent
from app.models.user import User
from tests.factories import AdminFactory, RecruitmentEventFactory, UserFactory


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


async def _create_event(db: AsyncSession, user_id: int, validator_id: int | None = None, **kwargs) -> RecruitmentEvent:
    """Create a RecruitmentEvent and return it."""
    event = RecruitmentEventFactory.build(user_id=user_id, validator_id=validator_id, **kwargs)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


# =============================================================================
# List recruitment events
# =============================================================================


@pytest.mark.asyncio
async def test_list_recruitment_events_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET, nickname="CadetAlpha")
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    await _create_event(db_session, user_id=cadet.id, validator_id=admin.id)
    await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_PRESENTATION)

    # WHEN
    response = await client.get("/api/admin/recruitment", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 2
    item = data["items"][0]
    assert "type" in item
    assert "type_as_string" in item
    assert "user_nickname" in item
    assert "validator_nickname" in item


@pytest.mark.asyncio
async def test_list_recruitment_events_search_by_cadet_nickname(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet1 = UserFactory.build(status=User.STATUS_CADET, nickname="AlphaWolf")
    cadet2 = UserFactory.build(status=User.STATUS_CADET, nickname="BravoBear")
    db_session.add_all([cadet1, cadet2])
    await db_session.commit()
    await db_session.refresh(cadet1)
    await db_session.refresh(cadet2)
    await _create_event(db_session, user_id=cadet1.id, validator_id=admin.id)
    await _create_event(db_session, user_id=cadet2.id, validator_id=admin.id)

    # WHEN
    response = await client.get("/api/admin/recruitment?search=Alpha", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["user_nickname"] == "AlphaWolf"


@pytest.mark.asyncio
async def test_list_recruitment_events_filter_by_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_ACTIVITY)
    await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_PRESENTATION)

    # WHEN
    response = await client.get(f"/api/admin/recruitment?type={RecruitmentEvent.TYPE_ACTIVITY}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == RecruitmentEvent.TYPE_ACTIVITY


@pytest.mark.asyncio
async def test_list_recruitment_events_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    for _ in range(5):
        await _create_event(db_session, user_id=cadet.id, validator_id=admin.id)

    # WHEN
    response = await client.get("/api/admin/recruitment?skip=2&limit=2", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_recruitment_events_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.get("/api/admin/recruitment")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_recruitment_events_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/recruitment", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Update recruitment event
# =============================================================================


@pytest.mark.asyncio
async def test_update_recruitment_event_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    event = await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, comment="old comment")

    # WHEN
    response = await client.put(
        f"/api/admin/recruitment/{event.id}",
        headers=headers,
        json={"comment": "updated comment", "event_at": "2026-01-15T14:30:00Z"},
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == "updated comment"
    assert "2026-01-15" in data["event_at"]


@pytest.mark.asyncio
async def test_update_recruitment_event_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put(
        "/api/admin/recruitment/9999",
        headers=headers,
        json={"comment": "test"},
    )

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_recruitment_event_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.put("/api/admin/recruitment/1", json={"comment": "test"})

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_recruitment_event_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.put("/api/admin/recruitment/1", headers=headers, json={"comment": "test"})

    # THEN
    assert response.status_code == 403


# =============================================================================
# Delete recruitment event
# =============================================================================


@pytest.mark.asyncio
async def test_delete_recruitment_event_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    event = await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_GUEST)

    # WHEN
    response = await client.delete(f"/api/admin/recruitment/{event.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    result = await db_session.execute(select(RecruitmentEvent).where(RecruitmentEvent.id == event.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_activity_event_decrements_cadet_flights(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET, cadet_flights=3)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    event = await _create_event(db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_ACTIVITY)

    # WHEN
    response = await client.delete(f"/api/admin/recruitment/{event.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(cadet)
    assert cadet.cadet_flights == 2


@pytest.mark.asyncio
async def test_delete_presentation_event_restores_need_presentation(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    cadet = UserFactory.build(status=User.STATUS_CADET, need_presentation=False)
    db_session.add(cadet)
    await db_session.commit()
    await db_session.refresh(cadet)
    event = await _create_event(
        db_session, user_id=cadet.id, validator_id=admin.id, type=RecruitmentEvent.TYPE_PRESENTATION
    )

    # WHEN
    response = await client.delete(f"/api/admin/recruitment/{event.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(cadet)
    assert cadet.need_presentation is True


@pytest.mark.asyncio
async def test_delete_recruitment_event_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/recruitment/9999", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_recruitment_event_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.delete("/api/admin/recruitment/1")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_recruitment_event_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.delete("/api/admin/recruitment/1", headers=headers)

    # THEN
    assert response.status_code == 403
