import os

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.config import settings
from app.database import get_db
from app.models.calendar import CalendarEvent
from app.models.content import File
from app.models.module import Module
from app.models.user import User
from app.schemas.content import AdminFileListOut, AdminFileOut

router = APIRouter(prefix="/admin/files", tags=["admin-files"])


def _delete_file_from_disk(file: File) -> None:
    """Remove a file from disk storage. Silently ignores missing files."""
    file_path = os.path.join(settings.UPLOAD_DIR, file.uuid[0], file.uuid[1], f"{file.uuid}.{file.extension}")
    if os.path.exists(file_path):
        os.remove(file_path)


def _build_admin_file_out(file: File) -> AdminFileOut:
    """Build an AdminFileOut DTO from a File model instance."""
    return AdminFileOut(
        id=file.id,
        uuid=file.uuid,
        type=file.type,
        type_as_string=file.type_as_string,
        mime_type=file.mime_type,
        size=file.size,
        original_name=file.original_name,
        description=file.description,
        extension=file.extension,
        created_at=file.created_at,
        owner_id=file.owner_id,
        owner_nickname=file.owner.nickname if file.owner else None,
    )


@router.get("", response_model=AdminFileListOut)
async def list_files(
    search: str | None = Query(None),
    type_filter: int | None = Query(None, alias="type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(File)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                File.original_name.ilike(pattern),
                File.uuid.ilike(pattern),
            )
        )

    if type_filter is not None:
        query = query.where(File.type == type_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page
    query = (
        query.options(selectinload(File.owner))
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    files = result.scalars().all()

    return AdminFileListOut(
        items=[_build_admin_file_out(f) for f in files],
        total=total,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier non trouvé")

    # Nullify all FK references to this file
    await db.execute(update(CalendarEvent).where(CalendarEvent.image_id == file_id).values(image_id=None))
    await db.execute(update(Module).where(Module.image_id == file_id).values(image_id=None))
    await db.execute(update(Module).where(Module.image_header_id == file_id).values(image_header_id=None))

    # Delete from disk
    _delete_file_from_disk(file)

    # Delete from DB
    await db.delete(file)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
