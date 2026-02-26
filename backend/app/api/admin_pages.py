from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.content import Page, PageBlock
from app.models.user import User
from app.schemas.content import (
    AdminPageListOut,
    AdminPageOut,
    PageBlockCreate,
    PageBlockOut,
    PageBlockUpdate,
    PageCreate,
    PageUpdate,
)

router = APIRouter(prefix="/admin/pages", tags=["admin-pages"])


def _build_admin_page_out(page: Page, include_blocks: bool = True) -> AdminPageOut:
    """Build an AdminPageOut DTO from a Page model instance."""
    blocks = []
    if include_blocks:
        blocks = [
            PageBlockOut(id=b.id, type=b.type, content=b.content, number=b.number, enabled=b.enabled)
            for b in sorted(page.blocks, key=lambda b: b.number)
        ]
    return AdminPageOut(
        id=page.id,
        route=page.route,
        path=page.path,
        title=page.title,
        enabled=page.enabled,
        restriction=page.restriction,
        created_at=page.created_at,
        updated_at=page.updated_at,
        blocks=blocks,
    )


def _normalize_block_numbers(page: Page) -> None:
    """Re-sequence all blocks to 1, 2, 3... based on current number order."""
    sorted_blocks = sorted(page.blocks, key=lambda b: b.number)
    for i, block in enumerate(sorted_blocks, start=1):
        block.number = i


# --- Page endpoints ---


@router.get("", response_model=AdminPageListOut)
async def list_pages(
    search: str | None = Query(None),
    enabled: bool | None = Query(None),
    restriction: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Page)

    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Page.title.ilike(pattern), Page.route.ilike(pattern), Page.path.ilike(pattern)))

    if enabled is not None:
        query = query.where(Page.enabled == enabled)

    if restriction is not None:
        query = query.where(Page.restriction == restriction)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page (no blocks for list view)
    query = query.order_by(Page.title.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    pages = result.scalars().all()

    return AdminPageListOut(
        items=[_build_admin_page_out(p, include_blocks=False) for p in pages],
        total=total,
    )


@router.post("", response_model=AdminPageOut, status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(UTC)
    page = Page(
        title=data.title,
        route=data.route,
        path=data.path,
        enabled=data.enabled,
        restriction=data.restriction,
        created_at=now,
        updated_at=now,
    )

    try:
        db.add(page)
        await db.commit()
        await db.refresh(page)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une page avec cette route ou ce chemin existe déjà",
        )

    # Reload with blocks relationship
    result = await db.execute(select(Page).where(Page.id == page.id).options(selectinload(Page.blocks)))
    page = result.scalar_one()
    return _build_admin_page_out(page)


@router.get("/{page_id}", response_model=AdminPageOut)
async def get_page(
    page_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Page).where(Page.id == page_id).options(selectinload(Page.blocks)))
    page = result.scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page non trouvée")
    return _build_admin_page_out(page)


@router.put("/{page_id}", response_model=AdminPageOut)
async def update_page(
    page_id: int,
    data: PageUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Page).where(Page.id == page_id).options(selectinload(Page.blocks)))
    page = result.scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page non trouvée")

    page.title = data.title
    page.route = data.route
    page.path = data.path
    page.enabled = data.enabled
    page.restriction = data.restriction
    page.updated_at = datetime.now(UTC)

    try:
        await db.commit()
        await db.refresh(page)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une page avec cette route ou ce chemin existe déjà",
        )

    result = await db.execute(select(Page).where(Page.id == page.id).options(selectinload(Page.blocks)))
    page = result.scalar_one()
    return _build_admin_page_out(page)


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Page).where(Page.id == page_id).options(selectinload(Page.blocks)))
    page = result.scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page non trouvée")

    await db.delete(page)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Block endpoints ---


async def _get_page_with_blocks(page_id: int, db: AsyncSession) -> Page:
    """Fetch a page with eager-loaded blocks or raise 404."""
    result = await db.execute(select(Page).where(Page.id == page_id).options(selectinload(Page.blocks)))
    page = result.scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page non trouvée")
    return page


@router.post("/{page_id}/blocks", response_model=AdminPageOut, status_code=status.HTTP_201_CREATED)
async def create_block(
    page_id: int,
    data: PageBlockCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    page = await _get_page_with_blocks(page_id, db)

    block = PageBlock(
        type=PageBlock.TYPE_MARKDOWN,
        content=data.content,
        number=data.number,
        enabled=data.enabled,
        page_id=page.id,
    )
    db.add(block)
    page.blocks.append(block)
    _normalize_block_numbers(page)
    page.updated_at = datetime.now(UTC)

    await db.commit()

    page = await _get_page_with_blocks(page_id, db)
    return _build_admin_page_out(page)


@router.put("/{page_id}/blocks/{block_id}", response_model=AdminPageOut)
async def update_block(
    page_id: int,
    block_id: int,
    data: PageBlockUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    page = await _get_page_with_blocks(page_id, db)

    block = next((b for b in page.blocks if b.id == block_id), None)
    if block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloc non trouvé")

    block.content = data.content
    block.number = data.number
    block.enabled = data.enabled
    _normalize_block_numbers(page)
    page.updated_at = datetime.now(UTC)

    await db.commit()

    page = await _get_page_with_blocks(page_id, db)
    return _build_admin_page_out(page)


@router.delete("/{page_id}/blocks/{block_id}", response_model=AdminPageOut)
async def delete_block(
    page_id: int,
    block_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    page = await _get_page_with_blocks(page_id, db)

    block = next((b for b in page.blocks if b.id == block_id), None)
    if block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloc non trouvé")

    page.blocks.remove(block)
    await db.delete(block)
    _normalize_block_numbers(page)
    page.updated_at = datetime.now(UTC)

    await db.commit()

    page = await _get_page_with_blocks(page_id, db)
    return _build_admin_page_out(page)
