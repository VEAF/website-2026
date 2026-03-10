"""Integration tests for roster endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.user import User, UserModule
from tests.factories import ModuleFactory, UserFactory


async def _create_user_with_modules(
    db: AsyncSession,
    *,
    modules_active_with_level: int = 0,
    modules_active_without_level: int = 0,
    modules_inactive: int = 0,
    user_kwargs: dict | None = None,
) -> User:
    """Create a user with various module configurations.

    - modules_active_with_level: active=True, level>0 (ROOKIE)
    - modules_active_without_level: active=True, level=0 (UNKNOWN)
    - modules_inactive: active=False
    """
    user = UserFactory.build(**(user_kwargs or {}))
    db.add(user)
    await db.flush()

    for i in range(modules_active_with_level + modules_active_without_level + modules_inactive):
        module = ModuleFactory.build()
        db.add(module)
        await db.flush()

        if i < modules_active_with_level:
            um = UserModule(user_id=user.id, module_id=module.id, active=True, level=UserModule.LEVEL_ROOKIE)
        elif i < modules_active_with_level + modules_active_without_level:
            um = UserModule(user_id=user.id, module_id=module.id, active=True, level=UserModule.LEVEL_UNKNOWN)
        else:
            um = UserModule(user_id=user.id, module_id=module.id, active=False, level=UserModule.LEVEL_UNKNOWN)
        db.add(um)

    await db.commit()
    await db.refresh(user)
    return user


# =============================================================================
# GET /api/roster/pilots — active_module_count
# =============================================================================


@pytest.mark.asyncio
async def test_roster_pilots_counts_all_active_modules(client: AsyncClient, db_session: AsyncSession):
    """active_module_count should include active modules regardless of level."""
    # GIVEN — a pilot with 9 active+leveled, 3 active+level_unknown, 1 inactive
    user = await _create_user_with_modules(
        db_session,
        modules_active_with_level=9,
        modules_active_without_level=3,
        modules_inactive=1,
    )

    # WHEN
    response = await client.get("/api/roster/pilots")

    # THEN
    assert response.status_code == 200
    pilots = response.json()
    pilot = next(p for p in pilots if p["id"] == user.id)
    # 9 + 3 = 12 active modules (inactive not counted)
    assert pilot["active_module_count"] == 12


@pytest.mark.asyncio
async def test_roster_pilots_counts_active_level_unknown_modules(client: AsyncClient, db_session: AsyncSession):
    """Modules with active=True and level=LEVEL_UNKNOWN (0) must be counted."""
    # GIVEN — a pilot with only level_unknown active modules
    user = await _create_user_with_modules(
        db_session,
        modules_active_with_level=0,
        modules_active_without_level=5,
    )

    # WHEN
    response = await client.get("/api/roster/pilots")

    # THEN
    assert response.status_code == 200
    pilots = response.json()
    pilot = next(p for p in pilots if p["id"] == user.id)
    assert pilot["active_module_count"] == 5


@pytest.mark.asyncio
async def test_roster_pilots_excludes_inactive_modules(client: AsyncClient, db_session: AsyncSession):
    """Inactive modules should never be counted, even with a level set."""
    # GIVEN — a pilot with only inactive modules
    user = await _create_user_with_modules(
        db_session,
        modules_active_with_level=0,
        modules_active_without_level=0,
        modules_inactive=4,
    )

    # WHEN
    response = await client.get("/api/roster/pilots")

    # THEN
    assert response.status_code == 200
    pilots = response.json()
    pilot = next(p for p in pilots if p["id"] == user.id)
    assert pilot["active_module_count"] == 0


@pytest.mark.asyncio
async def test_roster_pilots_zero_modules(client: AsyncClient, db_session: AsyncSession):
    """A pilot with no modules should show count 0."""
    # GIVEN
    user = await _create_user_with_modules(db_session)

    # WHEN
    response = await client.get("/api/roster/pilots")

    # THEN
    assert response.status_code == 200
    pilots = response.json()
    pilot = next(p for p in pilots if p["id"] == user.id)
    assert pilot["active_module_count"] == 0


@pytest.mark.asyncio
async def test_roster_pilots_group_filter(client: AsyncClient, db_session: AsyncSession):
    """Group filter should restrict which pilots are returned."""
    # GIVEN
    cadet = await _create_user_with_modules(
        db_session,
        modules_active_with_level=2,
        user_kwargs={"status": User.STATUS_CADET},
    )
    member = await _create_user_with_modules(
        db_session,
        modules_active_with_level=3,
        user_kwargs={"status": User.STATUS_MEMBER},
    )

    # WHEN — cadets only
    response = await client.get("/api/roster/pilots?group=cadets")

    # THEN
    assert response.status_code == 200
    pilots = response.json()
    ids = [p["id"] for p in pilots]
    assert cadet.id in ids
    assert member.id not in ids
