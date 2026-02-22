"""Integration tests for admin user endpoints."""

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


async def _create_user(db: AsyncSession, **kwargs) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


# =============================================================================
# List users
# =============================================================================


@pytest.mark.asyncio
async def test_list_users_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    user1 = UserFactory.build(nickname="alpha", email="alpha@test.com")
    user2 = UserFactory.build(nickname="bravo", email="bravo@test.com")
    db_session.add_all([user1, user2])
    await db_session.commit()

    # WHEN
    response = await client.get("/api/admin/users", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 3  # admin + 2 users
    # Verify AdminUserOut fields
    item = data["items"][0]
    assert "email" in item
    assert "roles" in item
    assert "status_as_string" in item
    assert "need_presentation" in item
    assert "cadet_flights" in item


@pytest.mark.asyncio
async def test_list_users_search(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    user1 = UserFactory.build(nickname="charlie", email="charlie@test.com")
    user2 = UserFactory.build(nickname="delta", email="delta@test.com")
    db_session.add_all([user1, user2])
    await db_session.commit()

    # WHEN
    response = await client.get("/api/admin/users?search=charlie", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nickname"] == "charlie"


@pytest.mark.asyncio
async def test_list_users_search_by_email(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    user1 = UserFactory.build(nickname="echo", email="specific@domain.com")
    user2 = UserFactory.build(nickname="foxtrot", email="other@domain.com")
    db_session.add_all([user1, user2])
    await db_session.commit()

    # WHEN
    response = await client.get("/api/admin/users?search=specific", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "specific@domain.com"


@pytest.mark.asyncio
async def test_list_users_status_filter(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    member = UserFactory.build(status=User.STATUS_MEMBER)
    cadet = UserFactory.build(status=User.STATUS_CADET)
    db_session.add_all([member, cadet])
    await db_session.commit()

    # WHEN
    response = await client.get(f"/api/admin/users?status={User.STATUS_CADET}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == User.STATUS_CADET


@pytest.mark.asyncio
async def test_list_users_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    for i in range(5):
        db_session.add(UserFactory.build())
    await db_session.commit()

    # WHEN
    response = await client.get("/api/admin/users?skip=2&limit=2", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6  # admin + 5 users
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_users_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.get("/api/admin/users")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/users", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get user detail
# =============================================================================


@pytest.mark.asyncio
async def test_get_user_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    target = UserFactory.build(nickname="golf", email="golf@test.com", discord="golf#1234")
    db_session.add(target)
    await db_session.commit()
    await db_session.refresh(target)

    # WHEN
    response = await client.get(f"/api/admin/users/{target.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target.id
    assert data["nickname"] == "golf"
    assert data["email"] == "golf@test.com"
    assert data["discord"] == "golf#1234"
    assert "roles" in data
    assert "status_as_string" in data


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/users/9999", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/users/1", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Update user
# =============================================================================


@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    target = UserFactory.build(
        nickname="hotel",
        email="hotel@test.com",
        status=User.STATUS_MEMBER,
        sim_dcs=True,
        sim_bms=False,
    )
    db_session.add(target)
    await db_session.commit()
    await db_session.refresh(target)

    # WHEN
    response = await client.put(f"/api/admin/users/{target.id}", json={
        "email": "updated@test.com",
        "nickname": "hotel-updated",
        "roles": ["ROLE_USER", "ROLE_ADMIN"],
        "status": User.STATUS_PRESIDENT,
        "discord": "new-discord",
        "forum": "new-forum",
        "sim_dcs": False,
        "sim_bms": True,
        "need_presentation": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@test.com"
    assert data["nickname"] == "hotel-updated"
    assert "ROLE_ADMIN" in data["roles"]
    assert data["status"] == User.STATUS_PRESIDENT
    assert data["status_as_string"] == "président"
    assert data["discord"] == "new-discord"
    assert data["forum"] == "new-forum"
    assert data["sim_dcs"] is False
    assert data["sim_bms"] is True
    assert data["need_presentation"] is True


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/users/9999", json={
        "email": "test@test.com",
        "nickname": "test",
        "roles": ["ROLE_USER"],
        "status": User.STATUS_MEMBER,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    existing = UserFactory.build(email="taken@test.com")
    target = UserFactory.build(email="original@test.com")
    db_session.add_all([existing, target])
    await db_session.commit()
    await db_session.refresh(target)

    # WHEN
    response = await client.put(f"/api/admin/users/{target.id}", json={
        "email": "taken@test.com",
        "nickname": target.nickname,
        "roles": ["ROLE_USER"],
        "status": target.status,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_user_duplicate_nickname(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    existing = UserFactory.build(nickname="taken-nick")
    target = UserFactory.build(nickname="original-nick")
    db_session.add_all([existing, target])
    await db_session.commit()
    await db_session.refresh(target)

    # WHEN
    response = await client.put(f"/api/admin/users/{target.id}", json={
        "email": target.email,
        "nickname": "taken-nick",
        "roles": ["ROLE_USER"],
        "status": target.status,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_user_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.put("/api/admin/users/1", json={
        "email": "test@test.com",
        "nickname": "test",
        "roles": ["ROLE_USER"],
        "status": User.STATUS_MEMBER,
    })

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.put("/api/admin/users/1", json={
        "email": "test@test.com",
        "nickname": "test",
        "roles": ["ROLE_USER"],
        "status": User.STATUS_MEMBER,
    }, headers=headers)

    # THEN
    assert response.status_code == 403
