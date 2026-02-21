import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.module import Module
from app.models.user import User, UserModule

router = APIRouter(prefix="/mission-maker", tags=["mission-maker"])


@router.get("/matrix")
async def get_matrix(
    group: str = "all",
    map_id: int | None = None,
    period: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Get users
    user_query = select(User).options(selectinload(User.modules).selectinload(UserModule.module))
    if group == "members":
        user_query = user_query.where(User.status.in_(User.STATUSES_MEMBER))
    elif group == "cadets":
        user_query = user_query.where(User.status == User.STATUS_CADET)
    elif group == "cadets-members":
        user_query = user_query.where(User.status.in_(User.STATUSES_MEMBER + [User.STATUS_CADET]))

    user_query = user_query.order_by(User.nickname)
    result = await db.execute(user_query)
    users = result.scalars().all()

    # Get modules (aircraft/helicopter)
    mod_query = select(Module).where(Module.type.in_([Module.TYPE_AIRCRAFT, Module.TYPE_HELICOPTER]))
    if period is not None:
        mod_query = mod_query.where(Module.period == period)
    mod_query = mod_query.order_by(Module.name)
    result = await db.execute(mod_query)
    modules = result.scalars().all()

    # Build matrix
    matrix = []
    for u in users:
        user_modules = {um.module_id: um for um in u.modules}
        row = {
            "user_id": u.id,
            "nickname": u.nickname,
            "modules": {},
        }
        for m in modules:
            um = user_modules.get(m.id)
            row["modules"][m.code] = {
                "level": um.level if um and um.active else None,
                "active": um.active if um else False,
            }
        matrix.append(row)

    return {
        "modules": [{"id": m.id, "code": m.code, "name": m.name, "type": m.type} for m in modules],
        "matrix": matrix,
    }


@router.post("/export")
async def export_csv(
    group: str = "all",
    period: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    data = await get_matrix(group=group, period=period, db=db)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # Header
    header = ["Pilote"] + [m["code"] for m in data["modules"]]
    writer.writerow(header)

    # Rows
    for row in data["matrix"]:
        line = [row["nickname"]]
        for m in data["modules"]:
            info = row["modules"].get(m["code"], {})
            level = info.get("level")
            if level is not None:
                line.append(UserModule.LEVELS.get(level, ""))
            else:
                line.append("")
        writer.writerow(line)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mission-maker.csv"},
    )
