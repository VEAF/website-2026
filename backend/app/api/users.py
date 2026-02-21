from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User, UserModule
from app.schemas.user import UserMe, UserModuleOut, UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == user.id).options(selectinload(User.modules).selectinload(UserModule.module))
    )
    user = result.scalar_one()

    return UserMe(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        status=user.status,
        status_as_string=user.status_as_string,
        sim_dcs=user.sim_dcs,
        sim_bms=user.sim_bms,
        discord=user.discord,
        forum=user.forum,
        created_at=user.created_at,
        roles=user.get_roles_list(),
        need_presentation=user.need_presentation,
        cadet_flights=user.cadet_flights,
        modules=[
            UserModuleOut(
                id=um.id,
                module_id=um.module_id,
                module_name=um.module.name if um.module else None,
                module_code=um.module.code if um.module else None,
                module_long_name=um.module.long_name if um.module else None,
                module_type=um.module.type if um.module else None,
                active=um.active,
                level=um.level,
                level_as_string=um.level_as_string,
            )
            for um in user.modules
        ],
    )


@router.put("/me", response_model=UserPublic)
async def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.nickname is not None:
        # Check uniqueness
        existing = await db.execute(select(User).where(User.nickname == data.nickname, User.id != user.id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nickname already taken")
        user.nickname = data.nickname

    if data.discord is not None:
        user.discord = data.discord
    if data.forum is not None:
        user.forum = data.forum
    if data.sim_dcs is not None:
        user.sim_dcs = data.sim_dcs
    if data.sim_bms is not None:
        user.sim_bms = data.sim_bms

    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    return UserPublic(
        id=user.id,
        nickname=user.nickname,
        status=user.status,
        status_as_string=user.status_as_string,
        sim_dcs=user.sim_dcs,
        sim_bms=user.sim_bms,
        discord=user.discord,
        forum=user.forum,
        created_at=user.created_at,
    )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserPublic(
        id=user.id,
        nickname=user.nickname,
        status=user.status,
        status_as_string=user.status_as_string,
        sim_dcs=user.sim_dcs,
        sim_bms=user.sim_bms,
        discord=user.discord,
        forum=user.forum,
        created_at=user.created_at,
    )
