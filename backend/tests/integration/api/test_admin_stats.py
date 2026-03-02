"""Integration tests for admin stats endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.user import User
from tests.factories import AdminFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_stats_includes_cadets_ready_to_promote(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    ready_cadet = UserFactory.build(
        status=User.STATUS_CADET, sim_dcs=True, need_presentation=False, cadet_flights=5,
    )
    not_ready_cadet = UserFactory.build(
        status=User.STATUS_CADET, sim_dcs=False, need_presentation=True, cadet_flights=2,
    )
    db_session.add_all([ready_cadet, not_ready_cadet])
    await db_session.commit()

    # WHEN
    response = await client.get("/api/admin/stats", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["cadets_ready_to_promote"] == 1


@pytest.mark.asyncio
async def test_stats_cadets_ready_zero_when_none(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/stats", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["cadets_ready_to_promote"] == 0
