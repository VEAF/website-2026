from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Url
from app.schemas.content import UrlOut

router = APIRouter(prefix="/urls", tags=["urls"])


@router.get("/{slug}", response_model=UrlOut)
async def get_url(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url).where(Url.slug == slug, Url.status == True))  # noqa: E712
    url = result.scalar_one_or_none()
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return UrlOut.model_validate(url)
