from fastapi import APIRouter

router = APIRouter(prefix="/dcsbot", tags=["dcsbot"])


@router.get("/servers")
async def get_dcsbot_servers():
    # TODO: Implement DCSBot service integration with cache
    return {"servers": [], "stats": None, "active_players": 0}
