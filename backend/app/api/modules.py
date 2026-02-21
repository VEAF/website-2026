from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.module import Module, ModuleRole, ModuleSystem
from app.schemas.module import ModuleOut, ModuleRoleOut, ModuleSystemOut

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("", response_model=list[ModuleOut])
async def list_modules(type: int | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Module).options(
        selectinload(Module.roles),
        selectinload(Module.systems),
        selectinload(Module.image),
        selectinload(Module.image_header),
    )
    if type is not None:
        query = query.where(Module.type == type)

    query = query.order_by(Module.name)
    result = await db.execute(query)
    modules = result.scalars().all()

    return [
        ModuleOut(
            id=m.id, type=m.type, type_as_string=m.type_as_string,
            name=m.name, long_name=m.long_name, code=m.code,
            landing_page=m.landing_page, landing_page_number=m.landing_page_number,
            period=m.period, period_as_string=m.period_as_string,
            image_uuid=m.image.uuid if m.image else None,
            image_header_uuid=m.image_header.uuid if m.image_header else None,
            roles=[ModuleRoleOut.model_validate(r) for r in m.roles],
            systems=[ModuleSystemOut.model_validate(s) for s in m.systems],
        )
        for m in modules
    ]


@router.get("/{module_id}", response_model=ModuleOut)
async def get_module(module_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Module).where(Module.id == module_id).options(
            selectinload(Module.roles), selectinload(Module.systems),
            selectinload(Module.image), selectinload(Module.image_header),
        )
    )
    m = result.scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return ModuleOut(
        id=m.id, type=m.type, type_as_string=m.type_as_string,
        name=m.name, long_name=m.long_name, code=m.code,
        landing_page=m.landing_page, landing_page_number=m.landing_page_number,
        period=m.period, period_as_string=m.period_as_string,
        image_uuid=m.image.uuid if m.image else None,
        image_header_uuid=m.image_header.uuid if m.image_header else None,
        roles=[ModuleRoleOut.model_validate(r) for r in m.roles],
        systems=[ModuleSystemOut.model_validate(s) for s in m.systems],
    )


@router.get("/roles", response_model=list[ModuleRoleOut])
async def list_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModuleRole).order_by(ModuleRole.position))
    return [ModuleRoleOut.model_validate(r) for r in result.scalars().all()]


@router.get("/systems", response_model=list[ModuleSystemOut])
async def list_systems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModuleSystem).order_by(ModuleSystem.position))
    return [ModuleSystemOut.model_validate(s) for s in result.scalars().all()]
