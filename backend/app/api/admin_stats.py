from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.content import MenuItem, Page, Url
from app.models.module import Module
from app.models.user import User

router = APIRouter(prefix="/admin/stats", tags=["admin-stats"])


class AdminStats(BaseModel):
    modules: int = 0
    users: int = 0
    pages: int = 0
    urls: int = 0
    menu_items: int = 0


@router.get("", response_model=AdminStats)
async def get_stats(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(func.count()).select_from(Module))
    modules_count = result.scalar_one()

    result = await db.execute(select(func.count()).select_from(User))
    users_count = result.scalar_one()

    result = await db.execute(select(func.count()).select_from(Page))
    pages_count = result.scalar_one()

    result = await db.execute(select(func.count()).select_from(Url))
    urls_count = result.scalar_one()

    result = await db.execute(select(func.count()).select_from(MenuItem))
    menu_items_count = result.scalar_one()

    return AdminStats(modules=modules_count, users=users_count, pages=pages_count, urls=urls_count, menu_items=menu_items_count)
