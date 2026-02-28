"""Integration tests for user profile endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.module import Module
from app.models.user import User, UserModule
from tests.factories import ModuleFactory, UserFactory


async def _create_user(db: AsyncSession, **kwargs) -> User:
    """Create a user and return it."""
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_user_with_auth(db: AsyncSession, **kwargs) -> tuple[User, dict]:
    """Create a user and return (user, auth_headers)."""
    user = await _create_user(db, **kwargs)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_module(db: AsyncSession, **kwargs) -> Module:
    """Create a module and return it."""
    module = ModuleFactory.build(**kwargs)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@pytest.mark.asyncio
async def test_get_user_profile_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session, discord="pilot#1234", forum="pilot_forum")

    # WHEN
    response = await client.get(f"/api/users/{user.id}")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["nickname"] == user.nickname
    assert data["status"] == User.STATUS_MEMBER
    assert data["status_as_string"] == "membre"
    assert data["sim_dcs"] is True
    assert data["sim_bms"] is False
    assert data["discord"] == "pilot#1234"
    assert data["forum"] == "pilot_forum"
    assert data["created_at"] is not None
    assert data["modules"] == []


@pytest.mark.asyncio
async def test_get_user_profile_not_found(client: AsyncClient, db_session: AsyncSession):
    # WHEN
    response = await client.get("/api/users/99999")

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_profile_with_modules(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user = await _create_user(db_session)
    aircraft = await _create_module(db_session, type=Module.TYPE_AIRCRAFT, long_name="F-16C Viper", period=Module.PERIOD_MODERN)
    helicopter = await _create_module(db_session, type=Module.TYPE_HELICOPTER, long_name="Ka-50 Black Shark")

    um1 = UserModule(user_id=user.id, module_id=aircraft.id, active=True, level=UserModule.LEVEL_MISSION)
    um2 = UserModule(user_id=user.id, module_id=helicopter.id, active=False, level=UserModule.LEVEL_ROOKIE)
    db_session.add_all([um1, um2])
    await db_session.commit()

    # WHEN
    response = await client.get(f"/api/users/{user.id}")

    # THEN
    assert response.status_code == 200
    data = response.json()
    modules = data["modules"]
    assert len(modules) == 2

    # Find aircraft module in response
    aircraft_mod = next(m for m in modules if m["module_id"] == aircraft.id)
    assert aircraft_mod["module_name"] == aircraft.name
    assert aircraft_mod["module_long_name"] == "F-16C Viper"
    assert aircraft_mod["module_type"] == Module.TYPE_AIRCRAFT
    assert aircraft_mod["module_type_as_string"] == "Avion"
    assert aircraft_mod["module_period"] == Module.PERIOD_MODERN
    assert aircraft_mod["module_period_as_string"] == "MODERN"
    assert aircraft_mod["active"] is True
    assert aircraft_mod["level"] == UserModule.LEVEL_MISSION
    assert aircraft_mod["level_as_string"] == "mission"

    # Find helicopter module in response
    heli_mod = next(m for m in modules if m["module_id"] == helicopter.id)
    assert heli_mod["module_long_name"] == "Ka-50 Black Shark"
    assert heli_mod["module_type"] == Module.TYPE_HELICOPTER
    assert heli_mod["module_type_as_string"] == "Hélicoptère"
    assert heli_mod["active"] is False
    assert heli_mod["level"] == UserModule.LEVEL_ROOKIE
    assert heli_mod["level_as_string"] == "débutant"


@pytest.mark.asyncio
async def test_get_user_profile_no_auth_required(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — no auth headers
    user = await _create_user(db_session)

    # WHEN — call without Authorization header
    response = await client.get(f"/api/users/{user.id}")

    # THEN — public endpoint, should succeed
    assert response.status_code == 200
    assert response.json()["id"] == user.id


@pytest.mark.asyncio
async def test_get_me_with_modules_returns_module_period(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    user, headers = await _create_user_with_auth(db_session)
    aircraft = await _create_module(db_session, type=Module.TYPE_AIRCRAFT, long_name="F-16C Viper", period=Module.PERIOD_MODERN)
    helicopter = await _create_module(db_session, type=Module.TYPE_HELICOPTER, long_name="Ka-50 Black Shark")

    um1 = UserModule(user_id=user.id, module_id=aircraft.id, active=True, level=UserModule.LEVEL_MISSION)
    um2 = UserModule(user_id=user.id, module_id=helicopter.id, active=False, level=UserModule.LEVEL_ROOKIE)
    db_session.add_all([um1, um2])
    await db_session.commit()

    # WHEN
    response = await client.get("/api/users/me", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    modules = data["modules"]
    assert len(modules) == 2

    aircraft_mod = next(m for m in modules if m["module_id"] == aircraft.id)
    assert aircraft_mod["module_period"] == Module.PERIOD_MODERN
    assert aircraft_mod["module_period_as_string"] == "MODERN"

    heli_mod = next(m for m in modules if m["module_id"] == helicopter.id)
    assert heli_mod["module_period"] is None
    assert heli_mod["module_period_as_string"] == ""
