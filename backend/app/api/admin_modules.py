from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.module import Module, ModuleRole, ModuleSystem
from app.models.user import User
from app.schemas.module import (
    ModuleCreate,
    ModuleOut,
    ModuleRoleCreate,
    ModuleRoleOut,
    ModuleRoleUpdate,
    ModuleSystemCreate,
    ModuleSystemOut,
    ModuleSystemUpdate,
    ModuleUpdate,
)

router = APIRouter(prefix="/admin/modules", tags=["admin-modules"])


async def _build_module_out(module_id: int, db: AsyncSession) -> ModuleOut:
    """Fetch a module with eager-loaded relationships and build the output schema."""
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(
            selectinload(Module.roles),
            selectinload(Module.systems),
            selectinload(Module.image),
            selectinload(Module.image_header),
        )
    )
    m = result.scalar_one()
    return ModuleOut(
        id=m.id,
        type=m.type,
        type_as_string=m.type_as_string,
        name=m.name,
        long_name=m.long_name,
        code=m.code,
        landing_page=m.landing_page,
        landing_page_number=m.landing_page_number,
        period=m.period,
        period_as_string=m.period_as_string,
        image_uuid=m.image.uuid if m.image else None,
        image_header_uuid=m.image_header.uuid if m.image_header else None,
        roles=[ModuleRoleOut.model_validate(r) for r in m.roles],
        systems=[ModuleSystemOut.model_validate(s) for s in m.systems],
    )


# --- Module endpoints ---


@router.post("", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
async def create_module(
    data: ModuleCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    module = Module(
        type=data.type,
        name=data.name,
        long_name=data.long_name,
        code=data.code,
        landing_page=data.landing_page,
        landing_page_number=data.landing_page_number,
        period=data.period,
    )

    if data.role_ids:
        result = await db.execute(select(ModuleRole).where(ModuleRole.id.in_(data.role_ids)))
        module.roles = list(result.scalars().all())

    if data.system_ids:
        result = await db.execute(select(ModuleSystem).where(ModuleSystem.id.in_(data.system_ids)))
        module.systems = list(result.scalars().all())

    try:
        db.add(module)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un module avec ce nom ou ce code existe déjà",
        )

    return await _build_module_out(module.id, db)


@router.put("/{module_id}", response_model=ModuleOut)
async def update_module(
    module_id: int,
    data: ModuleUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(selectinload(Module.roles), selectinload(Module.systems))
    )
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module non trouvé")

    module.type = data.type
    module.name = data.name
    module.long_name = data.long_name
    module.code = data.code
    module.landing_page = data.landing_page
    module.landing_page_number = data.landing_page_number
    module.period = data.period

    if data.role_ids:
        result = await db.execute(select(ModuleRole).where(ModuleRole.id.in_(data.role_ids)))
        module.roles = list(result.scalars().all())
    else:
        module.roles = []

    if data.system_ids:
        result = await db.execute(select(ModuleSystem).where(ModuleSystem.id.in_(data.system_ids)))
        module.systems = list(result.scalars().all())
    else:
        module.systems = []

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un module avec ce nom ou ce code existe déjà",
        )

    return await _build_module_out(module.id, db)


# --- ModuleRole endpoints ---


@router.post("/roles", response_model=ModuleRoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: ModuleRoleCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    role = ModuleRole(name=data.name, code=data.code, position=data.position)
    try:
        db.add(role)
        await db.commit()
        await db.refresh(role)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un rôle avec ce nom ou ce code existe déjà",
        )
    return ModuleRoleOut.model_validate(role)


@router.put("/roles/{role_id}", response_model=ModuleRoleOut)
async def update_role(
    role_id: int,
    data: ModuleRoleUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    role = await db.get(ModuleRole, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    role.name = data.name
    role.code = data.code
    role.position = data.position

    try:
        await db.commit()
        await db.refresh(role)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un rôle avec ce nom ou ce code existe déjà",
        )
    return ModuleRoleOut.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    role = await db.get(ModuleRole, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    await db.delete(role)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- ModuleSystem endpoints ---


@router.post("/systems", response_model=ModuleSystemOut, status_code=status.HTTP_201_CREATED)
async def create_system(
    data: ModuleSystemCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    system = ModuleSystem(code=data.code, name=data.name, position=data.position)
    try:
        db.add(system)
        await db.commit()
        await db.refresh(system)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un système avec ce nom ou ce code existe déjà",
        )
    return ModuleSystemOut.model_validate(system)


@router.put("/systems/{system_id}", response_model=ModuleSystemOut)
async def update_system(
    system_id: int,
    data: ModuleSystemUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    system = await db.get(ModuleSystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Système non trouvé")

    system.code = data.code
    system.name = data.name
    system.position = data.position

    try:
        await db.commit()
        await db.refresh(system)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un système avec ce nom ou ce code existe déjà",
        )
    return ModuleSystemOut.model_validate(system)


@router.delete("/systems/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(
    system_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    system = await db.get(ModuleSystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Système non trouvé")

    await db.delete(system)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
