from fastapi import APIRouter

router = APIRouter(prefix="/teamspeak", tags=["teamspeak"])


@router.get("/status")
async def get_teamspeak_status():
    # TODO: Implement TeamSpeak client integration with cache
    return {"clients": [], "channels": [], "client_count": 0}
