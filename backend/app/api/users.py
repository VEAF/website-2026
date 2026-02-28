from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.module import Module
from app.models.user import User, UserModule
from app.schemas.user import (
    UserMe,
    UserModuleActiveUpdate,
    UserModuleLevelUpdate,
    UserModuleOut,
    UserModuleUpdateResponse,
    UserProfileOut,
    UserPublic,
    UserUpdate,
)

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
                module_period=um.module.period if um.module else None,
                active=um.active,
                level=um.level,
                level_as_string=um.level_as_string,
            )
            for um in user.modules
        ],
    )


@router.put("/me", response_model=UserPublic)
async def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.discord is not None:
        user.discord = data.discord
    if data.forum is not None:
        user.forum = data.forum
    if data.sim_dcs is not None:
        user.sim_dcs = data.sim_dcs
    if data.sim_bms is not None:
        user.sim_bms = data.sim_bms

    user.updated_at = datetime.now(UTC)
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


@router.put("/me/modules/{module_id}/level", response_model=UserModuleUpdateResponse)
async def update_my_module_level(
    module_id: int,
    data: UserModuleLevelUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    module = await db.get(Module, module_id)
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    if data.level == UserModule.LEVEL_INSTRUCTOR and not user.is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructor level is reserved for members")

    result = await db.execute(
        select(UserModule).where(UserModule.user_id == user.id, UserModule.module_id == module_id)
    )
    user_module = result.scalar_one_or_none()

    if data.level != UserModule.LEVEL_UNKNOWN:
        if user_module is None:
            user_module = UserModule(user_id=user.id, module_id=module_id)
            db.add(user_module)
        user_module.level = data.level
        user_module.active = True
        await db.commit()
        await db.refresh(user_module)
        return UserModuleUpdateResponse(
            module_id=module_id,
            active=user_module.active,
            level=user_module.level,
            level_as_string=user_module.level_as_string,
        )
    else:
        if user_module is not None:
            await db.delete(user_module)
            await db.commit()
        return UserModuleUpdateResponse(
            module_id=module_id, active=False, level=0, level_as_string="inconnu", deleted=True
        )


@router.put("/me/modules/{module_id}/active", response_model=UserModuleUpdateResponse)
async def update_my_module_active(
    module_id: int,
    data: UserModuleActiveUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    module = await db.get(Module, module_id)
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    result = await db.execute(
        select(UserModule).where(UserModule.user_id == user.id, UserModule.module_id == module_id)
    )
    user_module = result.scalar_one_or_none()

    if user_module is None:
        user_module = UserModule(user_id=user.id, module_id=module_id)
        if module.type in Module.TYPES_WITH_LEVEL:
            user_module.level = UserModule.LEVEL_ROOKIE
        else:
            user_module.level = UserModule.LEVEL_MISSION
        db.add(user_module)

    user_module.active = data.active
    await db.commit()
    await db.refresh(user_module)

    return UserModuleUpdateResponse(
        module_id=module_id,
        active=user_module.active,
        level=user_module.level,
        level_as_string=user_module.level_as_string,
    )


@router.get("/{user_id}", response_model=UserProfileOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.modules).selectinload(UserModule.module))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfileOut(
        id=user.id,
        nickname=user.nickname,
        status=user.status,
        status_as_string=user.status_as_string,
        sim_dcs=user.sim_dcs,
        sim_bms=user.sim_bms,
        discord=user.discord,
        forum=user.forum,
        created_at=user.created_at,
        modules=[
            UserModuleOut(
                id=um.id,
                module_id=um.module_id,
                module_name=um.module.name if um.module else None,
                module_code=um.module.code if um.module else None,
                module_long_name=um.module.long_name if um.module else None,
                module_type=um.module.type if um.module else None,
                module_period=um.module.period if um.module else None,
                active=um.active,
                level=um.level,
                level_as_string=um.level_as_string,
            )
            for um in user.modules
        ],
    )
