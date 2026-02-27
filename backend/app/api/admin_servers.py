from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.dcs import Server
from app.models.user import User
from app.schemas.dcs import AdminServerListOut, ServerCreate, ServerOut, ServerUpdate

router = APIRouter(prefix="/admin/servers", tags=["admin-servers"])


@router.get("", response_model=AdminServerListOut)
async def list_servers(
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Server)

    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Server.name.ilike(pattern), Server.code.ilike(pattern)))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Server.name.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    servers = result.scalars().all()

    return AdminServerListOut(
        items=[ServerOut.model_validate(s) for s in servers],
        total=total,
    )


@router.post("", response_model=ServerOut, status_code=status.HTTP_201_CREATED)
async def create_server(
    data: ServerCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    server = Server(
        name=data.name,
        code=data.code,
    )

    try:
        db.add(server)
        await db.commit()
        await db.refresh(server)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un serveur avec ce code existe déjà",
        )

    return ServerOut.model_validate(server)


@router.get("/{server_id}", response_model=ServerOut)
async def get_server(
    server_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    server = await db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur non trouvé")
    return ServerOut.model_validate(server)


@router.put("/{server_id}", response_model=ServerOut)
async def update_server(
    server_id: int,
    data: ServerUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    server = await db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur non trouvé")

    server.name = data.name
    server.code = data.code

    try:
        await db.commit()
        await db.refresh(server)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un serveur avec ce code existe déjà",
        )

    return ServerOut.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    server = await db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur non trouvé")

    await db.delete(server)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
