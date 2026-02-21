from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_optional_user
from app.auth.permissions import is_granted_to_level
from app.database import get_db
from app.models.content import Page, PageBlock
from app.models.user import User
from app.schemas.content import PageBlockOut, PageOut

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("/{slug:path}", response_model=PageOut)
async def get_page(slug: str, user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Page).where(Page.path == slug, Page.enabled == True)  # noqa: E712
        .options(selectinload(Page.blocks))
    )
    page = result.scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not is_granted_to_level(user, page.restriction):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return PageOut(
        id=page.id,
        route=page.route,
        path=page.path,
        title=page.title,
        enabled=page.enabled,
        restriction=page.restriction,
        created_at=page.created_at,
        updated_at=page.updated_at,
        blocks=[
            PageBlockOut(id=b.id, type=b.type, content=b.content, number=b.number, enabled=b.enabled)
            for b in page.blocks
            if b.enabled
        ],
    )
