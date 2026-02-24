from fastapi import APIRouter

from app.schemas.dcs import DcsBotPageOut, DcsBotServerOut, DcsBotStatsOut, MissionInfoOut, PlayerEntryOut
from app.services import dcsbot as dcsbot_service

router = APIRouter(prefix="/dcsbot", tags=["dcsbot"])


@router.get("/servers", response_model=DcsBotPageOut)
async def get_dcsbot_servers():
    servers_data = await dcsbot_service.get_servers()
    stats_data = await dcsbot_service.get_server_stats()

    if servers_data is None:
        return DcsBotPageOut(servers=[], stats=None)

    items = []
    for s in servers_data:
        mission_raw = s.get("mission")
        players_raw = s.get("players") or []
        items.append(
            DcsBotServerOut(
                name=s.get("name", ""),
                status=s.get("status", "Unknown"),
                num_players=len(players_raw),
                mission=MissionInfoOut(**mission_raw) if mission_raw else None,
                players=[PlayerEntryOut(**p) for p in players_raw],
            )
        )

    stats_out = None
    if stats_data:
        stats_out = DcsBotStatsOut(
            total_players=stats_data.get("totalPlayers", 0),
            active_players=stats_data.get("activePlayers", 0),
            total_sorties=stats_data.get("totalSorties", 0),
            avg_playtime=stats_data.get("avgPlaytime", 0),
            total_kills=stats_data.get("totalKills", 0),
            total_deaths=stats_data.get("totalDeaths", 0),
            total_pvp_kills=stats_data.get("totalPvPKills", 0),
            total_pvp_deaths=stats_data.get("totalPvPDeaths", 0),
        )

    return DcsBotPageOut(servers=items, stats=stats_out)
