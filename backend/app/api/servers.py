from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import can_control_server
from app.database import get_db
from app.models.dcs import Server
from app.models.user import User
from app.schemas.dcs import ServerOut

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("", response_model=list[ServerOut])
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).order_by(Server.name))
    return [ServerOut.model_validate(s) for s in result.scalars().all()]


@router.post("/{server_id}/control")
async def control_server(server_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not can_control_server(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    server = await db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # TODO: Implement server control via DCSBot API
    return {"detail": f"Control command sent to {server.name}"}
