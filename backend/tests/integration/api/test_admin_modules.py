"""Integration tests for admin module endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.module import Module, ModuleRole, ModuleSystem
from tests.factories import AdminFactory, ModuleFactory, ModuleRoleFactory, ModuleSystemFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


# =============================================================================
# Module CRUD
# =============================================================================


@pytest.mark.asyncio
async def test_create_module_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
        "landing_page": True,
        "landing_page_number": 1,
        "period": Module.PERIOD_MODERN,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "F16C"
    assert data["long_name"] == "F-16C Viper"
    assert data["code"] == "f16c"
    assert data["type"] == Module.TYPE_AIRCRAFT
    assert data["type_as_string"] == "Avion"
    assert data["landing_page"] is True
    assert data["landing_page_number"] == 1
    assert data["period"] == Module.PERIOD_MODERN
    assert data["period_as_string"] == "MODERN"


@pytest.mark.asyncio
async def test_create_module_with_roles_and_systems(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    role = ModuleRoleFactory.build()
    system = ModuleSystemFactory.build()
    db_session.add_all([role, system])
    await db_session.commit()
    await db_session.refresh(role)
    await db_session.refresh(system)

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "FA18C",
        "long_name": "F/A-18C Hornet",
        "code": "fa18c",
        "role_ids": [role.id],
        "system_ids": [system.id],
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert len(data["roles"]) == 1
    assert data["roles"][0]["code"] == role.code
    assert len(data["systems"]) == 1
    assert data["systems"][0]["code"] == system.code


@pytest.mark.asyncio
async def test_create_module_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
    })

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_module_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_module_duplicate_name(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    existing = ModuleFactory.build(name="F16C", code="f16c")
    db_session.add(existing)
    await db_session.commit()

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "Another F-16",
        "code": "f16x",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_module_duplicate_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    existing = ModuleFactory.build(name="F16C", code="f16c")
    db_session.add(existing)
    await db_session.commit()

    # WHEN
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16X",
        "long_name": "Another F-16",
        "code": "f16c",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_module_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = ModuleFactory.build()
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)

    # WHEN
    response = await client.put(f"/api/admin/modules/{module.id}", json={
        "type": Module.TYPE_HELICOPTER,
        "name": module.name,
        "long_name": "Updated Name",
        "code": module.code,
        "landing_page": True,
        "landing_page_number": 5,
        "period": Module.PERIOD_WW2,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["long_name"] == "Updated Name"
    assert data["type"] == Module.TYPE_HELICOPTER
    assert data["landing_page"] is True
    assert data["landing_page_number"] == 5
    assert data["period"] == Module.PERIOD_WW2


@pytest.mark.asyncio
async def test_update_module_roles_replacement(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    role1 = ModuleRoleFactory.build()
    role2 = ModuleRoleFactory.build()
    db_session.add_all([role1, role2])
    await db_session.commit()
    await db_session.refresh(role1)
    await db_session.refresh(role2)

    # Create module with role1
    response = await client.post("/api/admin/modules", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
        "role_ids": [role1.id],
    }, headers=headers)
    module_id = response.json()["id"]

    # WHEN - update to role2 only
    response = await client.put(f"/api/admin/modules/{module_id}", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
        "role_ids": [role2.id],
        "system_ids": [],
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["roles"]) == 1
    assert data["roles"][0]["id"] == role2.id


@pytest.mark.asyncio
async def test_update_module_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/modules/9999", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_module_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.put("/api/admin/modules/1", json={
        "type": Module.TYPE_AIRCRAFT,
        "name": "F16C",
        "long_name": "F-16C Viper",
        "code": "f16c",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# ModuleRole CRUD
# =============================================================================


@pytest.mark.asyncio
async def test_create_role_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/modules/roles", json={
        "name": "Pilote",
        "code": "pilot",
        "position": 1,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Pilote"
    assert data["code"] == "pilot"
    assert data["position"] == 1


@pytest.mark.asyncio
async def test_create_role_duplicate_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    role = ModuleRoleFactory.build(code="pilot")
    db_session.add(role)
    await db_session.commit()

    # WHEN
    response = await client.post("/api/admin/modules/roles", json={
        "name": "Another Pilot",
        "code": "pilot",
        "position": 2,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_role_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/modules/roles", json={
        "name": "Pilote",
        "code": "pilot",
        "position": 1,
    }, headers=headers)

    # THEN
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_role_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    role = ModuleRoleFactory.build()
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)

    # WHEN
    response = await client.put(f"/api/admin/modules/roles/{role.id}", json={
        "name": "Updated Role",
        "code": role.code,
        "position": 99,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Role"
    assert data["position"] == 99


@pytest.mark.asyncio
async def test_update_role_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/modules/roles/9999", json={
        "name": "Updated",
        "code": "updated",
        "position": 1,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_role_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    role = ModuleRoleFactory.build()
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)

    # WHEN
    response = await client.delete(f"/api/admin/modules/roles/{role.id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify deletion
    deleted = await db_session.get(ModuleRole, role.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_role_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/modules/roles/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# ModuleSystem CRUD
# =============================================================================


@pytest.mark.asyncio
async def test_create_system_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/modules/systems", json={
        "code": "radar",
        "name": "Radar",
        "position": 1,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "radar"
    assert data["name"] == "Radar"
    assert data["position"] == 1


@pytest.mark.asyncio
async def test_create_system_duplicate_code(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    system = ModuleSystemFactory.build(code="radar")
    db_session.add(system)
    await db_session.commit()

    # WHEN
    response = await client.post("/api/admin/modules/systems", json={
        "code": "radar",
        "name": "Another Radar",
        "position": 2,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_system_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    system = ModuleSystemFactory.build()
    db_session.add(system)
    await db_session.commit()
    await db_session.refresh(system)

    # WHEN
    response = await client.put(f"/api/admin/modules/systems/{system.id}", json={
        "code": system.code,
        "name": "Updated System",
        "position": 42,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated System"
    assert data["position"] == 42


@pytest.mark.asyncio
async def test_delete_system_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    system = ModuleSystemFactory.build()
    db_session.add(system)
    await db_session.commit()
    await db_session.refresh(system)

    # WHEN
    response = await client.delete(f"/api/admin/modules/systems/{system.id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify deletion
    deleted = await db_session.get(ModuleSystem, system.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_system_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/modules/systems/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Module Image Upload/Delete
# =============================================================================

FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # Minimal JPEG-like bytes


async def _create_module(db: AsyncSession) -> Module:
    """Create and return a module."""
    module = ModuleFactory.build()
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@pytest.mark.asyncio
async def test_upload_module_image_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["image_uuid"] is not None
    assert data["image_header_uuid"] is None


@pytest.mark.asyncio
async def test_upload_module_image_header_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(
        f"/api/admin/modules/{module.id}/image-header",
        files={"file": ("banner.png", FAKE_JPEG, "image/png")},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["image_header_uuid"] is not None
    assert data["image_uuid"] is None


@pytest.mark.asyncio
async def test_upload_module_image_replaces_previous(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # Upload first image
    resp1 = await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("first.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )
    first_uuid = resp1.json()["image_uuid"]

    # WHEN - upload second image
    resp2 = await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("second.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # THEN
    assert resp2.status_code == 200
    second_uuid = resp2.json()["image_uuid"]
    assert second_uuid is not None
    assert second_uuid != first_uuid


@pytest.mark.asyncio
async def test_upload_module_image_invalid_mime_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_module_image_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put(
        "/api/admin/modules/9999/image",
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_module_image_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # THEN
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_module_image_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # Upload an image first
    await client.put(
        f"/api/admin/modules/{module.id}/image",
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # WHEN
    response = await client.delete(f"/api/admin/modules/{module.id}/image", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["image_uuid"] is None


@pytest.mark.asyncio
async def test_delete_module_image_header_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # Upload a header image first
    await client.put(
        f"/api/admin/modules/{module.id}/image-header",
        files={"file": ("banner.jpg", FAKE_JPEG, "image/jpeg")},
        headers=headers,
    )

    # WHEN
    response = await client.delete(f"/api/admin/modules/{module.id}/image-header", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["image_header_uuid"] is None


@pytest.mark.asyncio
async def test_delete_module_image_no_image(client: AsyncClient, db_session: AsyncSession):
    # GIVEN - module with no image
    _, headers = await _create_admin(db_session)
    module = await _create_module(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/modules/{module.id}/image", headers=headers)

    # THEN - idempotent, returns 200
    assert response.status_code == 200
    data = response.json()
    assert data["image_uuid"] is None
