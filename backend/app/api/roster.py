from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, UserModule

router = APIRouter(prefix="/roster", tags=["roster"])


@router.get("")
async def get_roster(group: str = "all", db: AsyncSession = Depends(get_db)):
    query = select(User).options(selectinload(User.modules).selectinload(UserModule.module))

    if group == "cadets":
        query = query.where(User.status == User.STATUS_CADET)
    elif group == "members":
        query = query.where(User.status.in_(User.STATUSES_MEMBER))
    elif group == "cadets-members":
        query = query.where(User.status.in_(User.STATUSES_MEMBER + [User.STATUS_CADET]))
    elif group == "office":
        query = query.where(User.status.in_(User.STATUSES_OFFICE))
    # "all" = no filter

    query = query.order_by(User.nickname)
    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "id": u.id,
            "nickname": u.nickname,
            "status": u.status,
            "status_as_string": u.status_as_string,
            "sim_dcs": u.sim_dcs,
            "sim_bms": u.sim_bms,
            "modules": [
                {
                    "module_id": um.module_id,
                    "module_name": um.module.name if um.module else None,
                    "module_code": um.module.code if um.module else None,
                    "module_type": um.module.type if um.module else None,
                    "active": um.active,
                    "level": um.level,
                    "level_as_string": um.level_as_string,
                }
                for um in u.modules
            ],
        }
        for u in users
    ]
