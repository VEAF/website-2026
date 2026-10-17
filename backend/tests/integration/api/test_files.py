"""Integration tests for file upload and download endpoints."""

import io
import os
import threading

import pytest
from httpx import AsyncClient
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import files as files_api
from app.auth.jwt import create_access_token
from app.config import settings
from app.models.content import File
from tests.factories import FileFactory, UserFactory


async def _create_user(db: AsyncSession) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


def _make_image_bytes(fmt: str, size: tuple[int, int] = (2, 2), mode: str = "RGB") -> bytes:
    """Generate minimal valid image bytes in the given format."""
    buf = io.BytesIO()
    img = Image.new(mode, size)
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


# =============================================================================
# Upload
# =============================================================================


@pytest.mark.asyncio
async def test_upload_jpeg_converts_to_webp(client: AsyncClient, db_session: AsyncSession):
    """JPEG uploads should be converted to WebP."""
    # GIVEN
    user, headers = await _create_user(db_session)
    content = _make_image_bytes("JPEG")

    # WHEN
    response = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("photo.jpg", content, "image/jpeg")},
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["extension"] == "webp"
    assert data["mime_type"] == "image/webp"
    assert data["original_name"] == "photo.webp"
    assert data["type"] == File.TYPE_IMAGE

    # Verify file on disk is valid WebP
    file_path = os.path.join(settings.UPLOAD_DIR, data["uuid"][0], data["uuid"][1], f"{data['uuid']}.webp")
    assert os.path.exists(file_path)
    img = Image.open(file_path)
    assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_upload_png_converts_to_webp(client: AsyncClient, db_session: AsyncSession):
    """PNG uploads should be converted to WebP."""
    # GIVEN
    user, headers = await _create_user(db_session)
    content = _make_image_bytes("PNG", mode="RGBA")

    # WHEN
    response = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("image.png", content, "image/png")},
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["extension"] == "webp"
    assert data["mime_type"] == "image/webp"
    assert data["original_name"] == "image.webp"


@pytest.mark.asyncio
async def test_upload_webp_kept_as_is(client: AsyncClient, db_session: AsyncSession):
    """WebP uploads should be stored as-is without re-encoding."""
    # GIVEN
    user, headers = await _create_user(db_session)
    content = _make_image_bytes("WEBP")

    # WHEN
    response = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("photo.webp", content, "image/webp")},
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["extension"] == "webp"
    assert data["mime_type"] == "image/webp"
    assert data["original_name"] == "photo.webp"
    assert data["type"] == File.TYPE_IMAGE


@pytest.mark.asyncio
async def test_upload_pdf_kept_as_is(client: AsyncClient, db_session: AsyncSession):
    """PDF uploads should be stored without conversion."""
    # GIVEN
    user, headers = await _create_user(db_session)
    pdf_content = b"%PDF-1.4 fake pdf content"

    # WHEN
    response = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("document.pdf", pdf_content, "application/pdf")},
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["extension"] == "pdf"
    assert data["mime_type"] == "application/pdf"
    assert data["type"] == File.TYPE_PDF


@pytest.mark.asyncio
async def test_upload_unsupported_type_rejected(client: AsyncClient, db_session: AsyncSession):
    """Unsupported MIME types should return 415."""
    # GIVEN
    user, headers = await _create_user(db_session)

    # WHEN
    response = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("script.sh", b"#!/bin/bash", "text/x-shellscript")},
    )

    # THEN
    assert response.status_code == 415


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content",
    [b"not an image at all", _make_image_bytes("PNG", size=(64, 64))[:60]],
    ids=["garbage", "truncated"],
)
async def test_upload_unreadable_image_rejected(client: AsyncClient, db_session: AsyncSession, content: bytes):
    """A file announced as an image that cannot be decoded is a client error, not a server error."""
    # GIVEN
    user, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/files", headers=headers, files={"file": ("image.png", content, "image/png")})

    # THEN
    assert response.status_code == 400
    result = await db_session.execute(select(File).where(File.owner_id == user.id))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_upload_image_over_pixel_limit_rejected(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
):
    """An image whose decoded size exceeds the pixel cap is refused before decoding."""
    # GIVEN
    user, headers = await _create_user(db_session)
    monkeypatch.setattr(files_api, "MAX_IMAGE_PIXELS", 100)
    content = _make_image_bytes("PNG", size=(20, 20))

    # WHEN
    response = await client.post("/api/files", headers=headers, files={"file": ("big.png", content, "image/png")})

    # THEN
    assert response.status_code == 413
    result = await db_session.execute(select(File).where(File.owner_id == user.id))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_upload_conversion_runs_off_event_loop(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
):
    """The WebP conversion must not run on the event loop thread (single worker: it would block the site)."""
    # GIVEN
    user, headers = await _create_user(db_session)
    loop_thread = threading.get_ident()
    seen_threads: list[int] = []
    original = files_api._to_webp

    def spy(raw: bytes) -> bytes:
        seen_threads.append(threading.get_ident())
        return original(raw)

    monkeypatch.setattr(files_api, "_to_webp", spy)

    # WHEN
    response = await client.post(
        "/api/files", headers=headers, files={"file": ("photo.jpg", _make_image_bytes("JPEG"), "image/jpeg")}
    )

    # THEN
    assert response.status_code == 201
    assert len(seen_threads) == 1
    assert seen_threads[0] != loop_thread


@pytest.mark.asyncio
async def test_upload_unauthenticated(client: AsyncClient):
    """Upload without auth should return 401."""
    # WHEN
    response = await client.post(
        "/api/files",
        files={"file": ("photo.jpg", b"fake", "image/jpeg")},
    )

    # THEN
    assert response.status_code == 401


# =============================================================================
# Download
# =============================================================================


@pytest.mark.asyncio
async def test_download_after_upload(client: AsyncClient, db_session: AsyncSession):
    """Uploaded and converted file should be downloadable."""
    # GIVEN
    user, headers = await _create_user(db_session)
    content = _make_image_bytes("JPEG")

    upload_resp = await client.post(
        "/api/files",
        headers=headers,
        files={"file": ("photo.jpg", content, "image/jpeg")},
    )
    assert upload_resp.status_code == 201
    uuid = upload_resp.json()["uuid"]

    # WHEN
    response = await client.get(f"/api/files/{uuid}")

    # THEN
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/webp"
    # Verify it's a valid WebP
    img = Image.open(io.BytesIO(response.content))
    assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_download_not_found(client: AsyncClient):
    """Download with unknown UUID should return 404."""
    # WHEN
    response = await client.get("/api/files/nonexistent-uuid")

    # THEN
    assert response.status_code == 404
