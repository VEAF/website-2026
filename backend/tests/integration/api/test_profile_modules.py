"""Integration tests for profile module level/active endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.module import Module
from app.models.user import User, UserModule
from tests.factories import ModuleFactory, UserFactory


async def _create_user(db: AsyncSession, **kwargs) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_module(db: AsyncSession, **kwargs) -> Module:
    """Create a module and return it."""
    module = ModuleFactory.build(**kwargs)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


# =============================================================================
# Update module level
# =============================================================================


@pytest.mark.asyncio
async def test_update_level_creates_user_module(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 1}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["module_id"] == module.id
    assert data["level"] == 1
    assert data["active"] is True
    assert data["deleted"] is False
    assert data["level_as_string"] == "débutant"


@pytest.mark.asyncio
async def test_update_level_updates_existing(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)
    um = UserModule(user_id=user.id, module_id=module.id, level=1, active=True)
    db_session.add(um)
    await db_session.commit()

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 2}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 2
    assert data["level_as_string"] == "mission"


@pytest.mark.asyncio
async def test_update_level_zero_deletes_user_module(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)
    um = UserModule(user_id=user.id, module_id=module.id, level=1, active=True)
    db_session.add(um)
    await db_session.commit()

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 0}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is True
    assert data["active"] is False
    assert data["level"] == 0

    # Verify deleted in DB
    result = await db_session.execute(
        select(UserModule).where(UserModule.user_id == user.id, UserModule.module_id == module.id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_update_level_zero_no_existing_record(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)

    # WHEN — setting level to 0 when no UserModule exists should be a no-op
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 0}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is True


@pytest.mark.asyncio
async def test_update_level_instructor_requires_member(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — cadet (not a member)
    user, headers = await _create_user(db_session, status=User.STATUS_CADET)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 3}, headers=headers)

    # THEN
    assert response.status_code == 403
    assert "members" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_level_instructor_member_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — member
    user, headers = await _create_user(db_session, status=User.STATUS_MEMBER)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 3}, headers=headers)

    # THEN
    assert response.status_code == 200
    assert response.json()["level"] == 3
    assert response.json()["level_as_string"] == "instructeur"


@pytest.mark.asyncio
async def test_update_level_module_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)

    # WHEN
    response = await client.put("/api/users/me/modules/99999/level", json={"level": 1}, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_level_unauthenticated(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 1})

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_level_invalid_value(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/level", json={"level": 5}, headers=headers)

    # THEN
    assert response.status_code == 422


# =============================================================================
# Update module active
# =============================================================================


@pytest.mark.asyncio
async def test_update_active_creates_with_rookie_for_aircraft(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session, type=Module.TYPE_AIRCRAFT)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/active", json={"active": True}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True
    assert data["level"] == 1  # ROOKIE default for aircraft
    assert data["level_as_string"] == "débutant"


@pytest.mark.asyncio
async def test_update_active_creates_with_mission_for_map(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session, type=Module.TYPE_MAP)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/active", json={"active": True}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True
    assert data["level"] == 2  # MISSION default for maps


@pytest.mark.asyncio
async def test_update_active_toggle_existing(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)
    module = await _create_module(db_session)
    um = UserModule(user_id=user.id, module_id=module.id, level=2, active=True)
    db_session.add(um)
    await db_session.commit()

    # WHEN — set active to false
    response = await client.put(f"/api/users/me/modules/{module.id}/active", json={"active": False}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False
    assert data["level"] == 2  # level unchanged


@pytest.mark.asyncio
async def test_update_active_module_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user(db_session)

    # WHEN
    response = await client.put("/api/users/me/modules/99999/active", json={"active": True}, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_active_unauthenticated(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(f"/api/users/me/modules/{module.id}/active", json={"active": True})

    # THEN
    assert response.status_code == 401
