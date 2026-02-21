from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dcs import Server

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/{server_code}")
async def get_map_data(server_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.code == server_code))
    server = result.scalar_one_or_none()
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # TODO: Implement map data retrieval
    return {"server": server.name, "theater": None, "clients": [], "bullseye": None}
