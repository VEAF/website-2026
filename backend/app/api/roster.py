from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.module import Module
from app.models.user import User, UserModule
from app.schemas.roster import (
    RosterModuleDetailOut,
    RosterModuleDetailUserOut,
    RosterModuleOut,
    RosterStatsOut,
    RosterUserOut,
)

router = APIRouter(prefix="/roster", tags=["roster"])


def _apply_group_filter(query: Select, group: str) -> Select:
    """Apply group filter on User.status."""
    if group == "cadets":
        query = query.where(User.status == User.STATUS_CADET)
    elif group == "members":
        query = query.where(User.status.in_(User.STATUSES_MEMBER))
    # "all" = no filter
    return query


@router.get("/stats", response_model=RosterStatsOut)
async def get_roster_stats(db: AsyncSession = Depends(get_db)):
    all_count = await db.scalar(select(func.count()).select_from(User))
    cadets_count = await db.scalar(select(func.count()).select_from(User).where(User.status == User.STATUS_CADET))
    members_count = await db.scalar(
        select(func.count()).select_from(User).where(User.status.in_(User.STATUSES_MEMBER))
    )
    return RosterStatsOut(all=all_count or 0, cadets=cadets_count or 0, members=members_count or 0)


@router.get("/pilots", response_model=list[RosterUserOut])
async def get_roster_pilots(group: str = "all", db: AsyncSession = Depends(get_db)):
    # Query users with a subquery count of active modules (active=true, level>0)
    active_module_count = (
        select(func.count())
        .where(UserModule.user_id == User.id, UserModule.active.is_(True), UserModule.level > 0)
        .correlate(User)
        .scalar_subquery()
    )
    query = select(User, active_module_count.label("active_module_count"))
    query = _apply_group_filter(query, group)
    query = query.order_by(User.nickname)
    result = await db.execute(query)

    return [
        RosterUserOut(
            id=u.id,
            nickname=u.nickname,
            status=u.status,
            status_as_string=u.status_as_string,
            active_module_count=count or 0,
        )
        for u, count in result.all()
    ]


@router.get("/modules/{module_id}", response_model=RosterModuleDetailOut)
async def get_roster_module_detail(module_id: int, group: str = "all", db: AsyncSession = Depends(get_db)):
    # Get module
    result = await db.execute(
        select(Module).options(selectinload(Module.image_header)).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Get user_modules for this module, filtered by group
    um_query = (
        select(UserModule)
        .join(User, UserModule.user_id == User.id)
        .options(selectinload(UserModule.user))
        .where(UserModule.module_id == module_id)
    )
    um_query = _apply_group_filter(um_query, group)
    um_query = um_query.order_by(User.nickname)

    um_result = await db.execute(um_query)
    user_modules = um_result.scalars().all()

    return RosterModuleDetailOut(
        module=RosterModuleOut(
            id=module.id,
            name=module.name,
            long_name=module.long_name,
            code=module.code,
            type=module.type,
            period=module.period,
            period_as_string=module.period_as_string,
            image_header_uuid=module.image_header.uuid if module.image_header else None,
            user_count=len(user_modules),
        ),
        users=[
            RosterModuleDetailUserOut(
                id=um.user.id,
                nickname=um.user.nickname,
                status=um.user.status,
                status_as_string=um.user.status_as_string,
                active=um.active,
                level=um.level,
                level_as_string=um.level_as_string,
            )
            for um in user_modules
        ],
    )


@router.get("/modules", response_model=list[RosterModuleOut])
async def get_roster_modules(type: int, group: str = "all", db: AsyncSession = Depends(get_db)):
    # Get modules of the requested type
    modules_query = select(Module).options(selectinload(Module.image_header)).where(Module.type == type)

    if type == Module.TYPE_AIRCRAFT:
        modules_query = modules_query.order_by(Module.period.desc(), Module.name.asc())
    else:
        modules_query = modules_query.order_by(Module.name.asc())

    result = await db.execute(modules_query)
    modules = result.scalars().all()

    # Count users per module filtered by group
    count_query = (
        select(UserModule.module_id, func.count(UserModule.user_id).label("cnt"))
        .join(User, UserModule.user_id == User.id)
        .join(Module, UserModule.module_id == Module.id)
        .where(Module.type == type)
    )
    count_query = _apply_group_filter(count_query, group)
    count_query = count_query.group_by(UserModule.module_id)

    count_result = await db.execute(count_query)
    counts = {row.module_id: row.cnt for row in count_result}

    return [
        RosterModuleOut(
            id=m.id,
            name=m.name,
            long_name=m.long_name,
            code=m.code,
            type=m.type,
            period=m.period,
            period_as_string=m.period_as_string,
            image_header_uuid=m.image_header.uuid if m.image_header else None,
            user_count=counts.get(m.id, 0),
        )
        for m in modules
    ]
