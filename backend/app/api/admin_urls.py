from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.content import Url
from app.models.user import User
from app.schemas.content import AdminUrlListOut, UrlCreate, UrlOut, UrlUpdate

router = APIRouter(prefix="/admin/urls", tags=["admin-urls"])


@router.get("", response_model=AdminUrlListOut)
async def list_urls(
    search: str | None = Query(None),
    status_filter: bool | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Url)

    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Url.slug.ilike(pattern), Url.target.ilike(pattern)))

    if status_filter is not None:
        query = query.where(Url.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Url.slug.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    urls = result.scalars().all()

    return AdminUrlListOut(
        items=[UrlOut.model_validate(u) for u in urls],
        total=total,
    )


@router.post("", response_model=UrlOut, status_code=status.HTTP_201_CREATED)
async def create_url(
    data: UrlCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(UTC)
    url = Url(
        slug=data.slug,
        target=data.target,
        delay=data.delay,
        status=data.status,
        created_at=now,
        updated_at=now,
    )

    try:
        db.add(url)
        await db.commit()
        await db.refresh(url)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une URL avec ce slug existe déjà",
        )

    return UrlOut.model_validate(url)


@router.get("/{url_id}", response_model=UrlOut)
async def get_url(
    url_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    url = await db.get(Url, url_id)
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL non trouvée")
    return UrlOut.model_validate(url)


@router.put("/{url_id}", response_model=UrlOut)
async def update_url(
    url_id: int,
    data: UrlUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    url = await db.get(Url, url_id)
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL non trouvée")

    url.slug = data.slug
    url.target = data.target
    url.delay = data.delay
    url.status = data.status
    url.updated_at = datetime.now(UTC)

    try:
        await db.commit()
        await db.refresh(url)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une URL avec ce slug existe déjà",
        )

    return UrlOut.model_validate(url)


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    url_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    url = await db.get(Url, url_id)
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL non trouvée")

    await db.delete(url)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
