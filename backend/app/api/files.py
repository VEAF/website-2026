import io
import os
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from PIL import Image, ImageOps
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.content import File
from app.models.user import User
from app.schemas.content import FileOut

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_UPLOAD_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}
CONVERTIBLE_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB


def _replace_extension(filename: str | None, new_ext: str) -> str | None:
    if not filename:
        return filename
    base, _ = os.path.splitext(filename)
    return f"{base}.{new_ext}"


@router.post("", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content_type = file.content_type or "application/octet-stream"

    if content_type not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Format non supporté")

    content = await file.read()

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Fichier trop volumineux (max 20 Mo)")

    # Convert JPEG/PNG to WebP; keep PDF and native WebP as-is
    if content_type in CONVERTIBLE_IMAGE_TYPES:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(content)))
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=85, method=6)
        content = buf.getvalue()
        extension = "webp"
        stored_mime = "image/webp"
        original_name = _replace_extension(file.filename, "webp")
    elif content_type == "image/webp":
        extension = "webp"
        stored_mime = "image/webp"
        original_name = file.filename
    else:
        extension = os.path.splitext(file.filename or "")[1].lstrip(".") or "bin"
        stored_mime = content_type
        original_name = file.filename

    file_uuid = str(uuid4())
    dir_path = os.path.join(settings.UPLOAD_DIR, file_uuid[0], file_uuid[1])
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{file_uuid}.{extension}")

    with open(file_path, "wb") as f:
        f.write(content)

    db_file = File(
        uuid=file_uuid,
        mime_type=stored_mime,
        size=len(content),
        extension=extension,
        original_name=original_name,
        type=File.type_from_mime(stored_mime),
        owner_id=user.id,
        created_at=datetime.now(UTC),
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return FileOut(
        id=db_file.id, uuid=db_file.uuid, type=db_file.type, type_as_string=db_file.type_as_string,
        mime_type=db_file.mime_type, size=db_file.size, original_name=db_file.original_name,
        description=db_file.description, extension=db_file.extension, created_at=db_file.created_at,
        owner_nickname=user.nickname,
    )


@router.get("/{file_uuid}")
async def download_file(file_uuid: str, db: AsyncSession = Depends(get_db)):
    # Strip optional extension (e.g. "uuid.webp" -> "uuid")
    file_uuid = file_uuid.rsplit(".", 1)[0] if "." in file_uuid else file_uuid
    result = await db.execute(select(File).where(File.uuid == file_uuid))
    db_file = result.scalar_one_or_none()
    if db_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    file_path = os.path.join(settings.UPLOAD_DIR, file_uuid[0], file_uuid[1], f"{file_uuid}.{db_file.extension}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    return FileResponse(file_path, media_type=db_file.mime_type, filename=db_file.original_name)
