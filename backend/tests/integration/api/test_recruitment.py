"""Integration tests for the member-facing recruitment endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.recruitment import RecruitmentEvent
from app.models.user import User
from tests.factories import AdminFactory, RecruitmentEventFactory, UserFactory

MEMBER_TYPES = [RecruitmentEvent.TYPE_PRESENTATION, RecruitmentEvent.TYPE_ACTIVITY]
ADMIN_ONLY_TYPES = [
    RecruitmentEvent.TYPE_TO_APPLY,
    RecruitmentEvent.TYPE_PROMOTE,
    RecruitmentEvent.TYPE_GUEST,
    RecruitmentEvent.TYPE_DISABLED,
]


async def _create_user(db: AsyncSession, factory=UserFactory, **kwargs) -> tuple:
    """Create a user and return (user, auth_headers)."""
    user = factory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _count_events(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count()).select_from(RecruitmentEvent).where(RecruitmentEvent.user_id == user_id)
    )
    return result.scalar_one()


# =============================================================================
# Read history
# =============================================================================


@pytest.mark.asyncio
async def test_history_anonymous_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)

    # WHEN
    response = await client.get(f"/api/recruitment/{cadet.id}")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [User.STATUS_UNKNOWN, User.STATUS_CADET, User.STATUS_GUEST])
async def test_history_non_member_forbidden(client: AsyncClient, db_session: AsyncSession, status: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    _, headers = await _create_user(db_session, status=status)

    # WHEN
    response = await client.get(f"/api/recruitment/{cadet.id}", headers=headers)

    # THEN
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_history_own_record_forbidden_for_cadet(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    cadet, headers = await _create_user(db_session, status=User.STATUS_CADET)

    # WHEN
    response = await client.get(f"/api/recruitment/{cadet.id}", headers=headers)

    # THEN
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "factory,status", [(UserFactory, User.STATUS_MEMBER), (AdminFactory, User.STATUS_UNKNOWN)], ids=["member", "admin"]
)
async def test_history_member_or_admin_allowed(client: AsyncClient, db_session: AsyncSession, factory, status: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    reader, headers = await _create_user(db_session, factory=factory, status=status)
    db_session.add(RecruitmentEventFactory.build(user_id=cadet.id, validator_id=reader.id, comment="RAS"))
    await db_session.commit()

    # WHEN
    response = await client.get(f"/api/recruitment/{cadet.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["comment"] == "RAS"
    assert data[0]["validator_nickname"] == reader.nickname


# =============================================================================
# Add event
# =============================================================================


@pytest.mark.asyncio
async def test_add_event_anonymous_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)

    # WHEN
    response = await client.post(f"/api/recruitment/{cadet.id}/events", params={"type": RecruitmentEvent.TYPE_ACTIVITY})

    # THEN
    assert response.status_code == 401
    assert await _count_events(db_session, cadet.id) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", [0, 7, 99, -1])
async def test_add_event_unknown_type_rejected(client: AsyncClient, db_session: AsyncSession, event_type: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    _, headers = await _create_user(db_session, factory=AdminFactory)

    # WHEN
    response = await client.post(f"/api/recruitment/{cadet.id}/events", params={"type": event_type}, headers=headers)

    # THEN
    assert response.status_code == 422
    assert await _count_events(db_session, cadet.id) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", MEMBER_TYPES + ADMIN_ONLY_TYPES)
async def test_add_event_unknown_status_forbidden(client: AsyncClient, db_session: AsyncSession, event_type: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    _, headers = await _create_user(db_session, status=User.STATUS_UNKNOWN)

    # WHEN
    response = await client.post(
        f"/api/recruitment/{cadet.id}/events", params={"type": event_type, "comment": "x"}, headers=headers
    )

    # THEN
    assert response.status_code == 403
    assert await _count_events(db_session, cadet.id) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", MEMBER_TYPES)
async def test_add_member_event_cadet_forbidden(client: AsyncClient, db_session: AsyncSession, event_type: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    _, headers = await _create_user(db_session, status=User.STATUS_CADET)

    # WHEN
    response = await client.post(f"/api/recruitment/{cadet.id}/events", params={"type": event_type}, headers=headers)

    # THEN
    assert response.status_code == 403
    assert await _count_events(db_session, cadet.id) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", ADMIN_ONLY_TYPES)
async def test_add_admin_only_event_member_forbidden(client: AsyncClient, db_session: AsyncSession, event_type: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    _, headers = await _create_user(db_session, status=User.STATUS_MEMBER)

    # WHEN
    response = await client.post(f"/api/recruitment/{cadet.id}/events", params={"type": event_type}, headers=headers)

    # THEN
    assert response.status_code == 403
    assert await _count_events(db_session, cadet.id) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", ADMIN_ONLY_TYPES)
async def test_add_admin_only_event_admin_allowed(client: AsyncClient, db_session: AsyncSession, event_type: int):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET)
    admin, headers = await _create_user(db_session, factory=AdminFactory)

    # WHEN
    response = await client.post(f"/api/recruitment/{cadet.id}/events", params={"type": event_type}, headers=headers)

    # THEN
    assert response.status_code == 200
    result = await db_session.execute(select(RecruitmentEvent).where(RecruitmentEvent.user_id == cadet.id))
    event = result.scalar_one()
    assert event.type == event_type
    assert event.validator_id == admin.id


@pytest.mark.asyncio
async def test_add_presentation_member_allowed(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET, need_presentation=True)
    _, headers = await _create_user(db_session, status=User.STATUS_MEMBER)

    # WHEN
    response = await client.post(
        f"/api/recruitment/{cadet.id}/events", params={"type": RecruitmentEvent.TYPE_PRESENTATION}, headers=headers
    )

    # THEN
    assert response.status_code == 200
    await db_session.refresh(cadet)
    assert cadet.need_presentation is False
    assert await _count_events(db_session, cadet.id) == 1


@pytest.mark.asyncio
async def test_add_activity_member_allowed(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    cadet, _ = await _create_user(db_session, status=User.STATUS_CADET, cadet_flights=2)
    _, headers = await _create_user(db_session, status=User.STATUS_MEMBER)

    # WHEN
    response = await client.post(
        f"/api/recruitment/{cadet.id}/events",
        params={"type": RecruitmentEvent.TYPE_ACTIVITY, "comment": "Vol de nuit"},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    await db_session.refresh(cadet)
    assert cadet.cadet_flights == 3
    result = await db_session.execute(select(RecruitmentEvent).where(RecruitmentEvent.user_id == cadet.id))
    assert result.scalar_one().comment == "Vol de nuit"


@pytest.mark.asyncio
async def test_add_event_unknown_target_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session, status=User.STATUS_MEMBER)

    # WHEN
    response = await client.post(
        "/api/recruitment/999999/events", params={"type": RecruitmentEvent.TYPE_ACTIVITY}, headers=headers
    )

    # THEN
    assert response.status_code == 404
