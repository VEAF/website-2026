"""Integration tests for admin file endpoints."""

import os

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.config import settings
from app.models.calendar import CalendarEvent
from app.models.content import File
from app.models.module import Module
from app.models.user import User
from tests.factories import AdminFactory, EventFactory, FileFactory, ModuleFactory, UserFactory


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


async def _create_file(db: AsyncSession, owner_id: int | None = None, **kwargs) -> File:
    """Create a File record and return it."""
    file = FileFactory.build(owner_id=owner_id, **kwargs)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


def _create_file_on_disk(file: File) -> str:
    """Create a fake file on disk for the given File model. Returns the file path."""
    dir_path = os.path.join(settings.UPLOAD_DIR, file.uuid[0], file.uuid[1])
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{file.uuid}.{file.extension}")
    with open(file_path, "wb") as f:
        f.write(b"fake content")
    return file_path


# =============================================================================
# List files
# =============================================================================


@pytest.mark.asyncio
async def test_list_files_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_file(db_session, owner_id=admin.id, original_name="photo.png")
    await _create_file(db_session, owner_id=admin.id, original_name="document.pdf")

    # WHEN
    response = await client.get("/api/admin/files", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 2
    item = data["items"][0]
    assert "uuid" in item
    assert "original_name" in item
    assert "type_as_string" in item
    assert "owner_nickname" in item


@pytest.mark.asyncio
async def test_list_files_search_by_name(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_file(db_session, owner_id=admin.id, original_name="mission_briefing.pdf")
    await _create_file(db_session, owner_id=admin.id, original_name="screenshot.png")

    # WHEN
    response = await client.get("/api/admin/files?search=briefing", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["original_name"] == "mission_briefing.pdf"


@pytest.mark.asyncio
async def test_list_files_search_by_uuid(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    file1 = await _create_file(db_session, owner_id=admin.id)
    await _create_file(db_session, owner_id=admin.id)

    # WHEN — search by first 8 chars of UUID
    search_term = file1.uuid[:8]
    response = await client.get(f"/api/admin/files?search={search_term}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    uuids = [item["uuid"] for item in data["items"]]
    assert file1.uuid in uuids


@pytest.mark.asyncio
async def test_list_files_filter_by_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    await _create_file(db_session, owner_id=admin.id, type=File.TYPE_IMAGE)
    await _create_file(db_session, owner_id=admin.id, type=File.TYPE_PDF, mime_type="application/pdf", extension="pdf")

    # WHEN
    response = await client.get(f"/api/admin/files?type={File.TYPE_PDF}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == File.TYPE_PDF


@pytest.mark.asyncio
async def test_list_files_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    for _ in range(5):
        await _create_file(db_session, owner_id=admin.id)

    # WHEN
    response = await client.get("/api/admin/files?skip=2&limit=2", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_files_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.get("/api/admin/files")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_files_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/files", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Delete file
# =============================================================================


@pytest.mark.asyncio
async def test_delete_file_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    file = await _create_file(db_session, owner_id=admin.id)
    disk_path = _create_file_on_disk(file)
    assert os.path.exists(disk_path)

    # WHEN
    response = await client.delete(f"/api/admin/files/{file.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    # File removed from DB
    result = await db_session.execute(select(File).where(File.id == file.id))
    assert result.scalar_one_or_none() is None
    # File removed from disk
    assert not os.path.exists(disk_path)


@pytest.mark.asyncio
async def test_delete_file_nullifies_event_image(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    file = await _create_file(db_session, owner_id=admin.id)
    event = EventFactory.build(owner_id=admin.id, image_id=file.id)
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    # WHEN
    response = await client.delete(f"/api/admin/files/{file.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(event)
    assert event.image_id is None


@pytest.mark.asyncio
async def test_delete_file_nullifies_module_images(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    admin, headers = await _create_admin(db_session)
    file_img = await _create_file(db_session, owner_id=admin.id)
    file_header = await _create_file(db_session, owner_id=admin.id)
    module = ModuleFactory.build(image_id=file_img.id, image_header_id=file_header.id)
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)

    # WHEN — delete the image file
    response = await client.delete(f"/api/admin/files/{file_img.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(module)
    assert module.image_id is None
    assert module.image_header_id == file_header.id  # untouched

    # WHEN — delete the header file
    response = await client.delete(f"/api/admin/files/{file_header.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    await db_session.refresh(module)
    assert module.image_header_id is None


@pytest.mark.asyncio
async def test_delete_file_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/files/9999", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_file_unauthenticated(client: AsyncClient):
    # GIVEN — no auth headers

    # WHEN
    response = await client.delete("/api/admin/files/1")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_file_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.delete("/api/admin/files/1", headers=headers)

    # THEN
    assert response.status_code == 403
