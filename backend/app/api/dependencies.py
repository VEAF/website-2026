"""Reusable FastAPI dependencies for resolving entities from path parameters.

Naming convention: `resolve_<entity>` or `resolve_<entity>_by_<field>`.
This avoids conflicts with route handler names (get_user, get_event, etc.)
and auth dependencies (get_current_user, require_admin, etc.).
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, UserModule


async def resolve_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    """Resolve a User by ID with modules eager-loaded, or raise 404."""
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.modules).selectinload(UserModule.module))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def resolve_user_by_nickname(nickname: str, db: AsyncSession = Depends(get_db)) -> User:
    """Resolve a User by nickname with modules eager-loaded, or raise 404."""
    result = await db.execute(
        select(User).where(User.nickname == nickname).options(selectinload(User.modules).selectinload(UserModule.module))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
