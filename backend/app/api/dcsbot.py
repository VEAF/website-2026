from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_optional_user
from app.models.user import User
from app.schemas.dcs import (
    DcsBotAttendanceOut,
    DcsBotPageOut,
    DcsBotServerDetailOut,
    DcsBotServerDetailPageOut,
    DcsBotServerOut,
    DcsBotStatsOut,
    MissionInfoOut,
    PlayerEntryOut,
    SunStateOut,
    TopMissionOut,
    TopModuleOut,
    TopTheatreOut,
    WeatherInfoOut,
)
from app.services import dcsbot as dcsbot_service
from app.services.sun_position import get_sun_state, parse_mission_datetime

router = APIRouter(prefix="/dcsbot", tags=["dcsbot"])


def _enrich_mission(mission_raw: dict | None) -> MissionInfoOut | None:
    """Build MissionInfoOut with sun state and formatted time fields."""
    if not mission_raw:
        return None
    mission = MissionInfoOut(**mission_raw)
    if mission.date_time:
        sun = get_sun_state(mission.date_time, mission.theatre)
        mission.sun_state = SunStateOut(**sun)
        dt = parse_mission_datetime(mission.date_time)
        if dt:
            mission.mission_time = dt.strftime("%H:%M")
            mission.mission_date_time = dt.strftime("%d/%m/%Y %H:%M")
    return mission


@router.get("/servers", response_model=DcsBotPageOut)
async def get_dcsbot_servers():
    servers_data = await dcsbot_service.get_servers()
    stats_data = await dcsbot_service.get_server_stats()

    if servers_data is None:
        return DcsBotPageOut(servers=[], stats=None)

    items = []
    for s in servers_data:
        players_raw = s.get("players") or []
        items.append(
            DcsBotServerOut(
                name=s.get("name", ""),
                status=s.get("status", "Unknown"),
                num_players=len(players_raw),
                mission=_enrich_mission(s.get("mission")),
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


def _build_stats(stats_data: dict) -> DcsBotStatsOut:
    """Build DcsBotStatsOut from DCSServerBot API response (camelCase keys)."""
    return DcsBotStatsOut(
        total_players=stats_data.get("totalPlayers", 0),
        active_players=stats_data.get("activePlayers", 0),
        total_sorties=stats_data.get("totalSorties", 0),
        avg_playtime=stats_data.get("avgPlaytime", 0),
        total_kills=stats_data.get("totalKills", 0),
        total_deaths=stats_data.get("totalDeaths", 0),
        total_pvp_kills=stats_data.get("totalPvPKills", 0),
        total_pvp_deaths=stats_data.get("totalPvPDeaths", 0),
    )


@router.get("/servers/{server_name}", response_model=DcsBotServerDetailPageOut)
async def get_dcsbot_server(
    server_name: str,
    user: User | None = Depends(get_optional_user),
):
    servers_data = await dcsbot_service.get_server(server_name)
    if not servers_data:
        raise HTTPException(status_code=404, detail="Serveur non trouvé")

    s = servers_data[0]
    players_raw = s.get("players") or []
    weather_raw = s.get("weather")

    # Only expose password to authenticated cadets and members
    password = s.get("password")
    if not (user and (user.is_cadet or user.is_member)):
        password = None

    server_out = DcsBotServerDetailOut(
        name=s.get("name", ""),
        status=s.get("status", "Unknown"),
        num_players=len(players_raw),
        address=s.get("address"),
        password=password,
        restart_time=str(s["restart_time"]) if s.get("restart_time") else None,
        mission=_enrich_mission(s.get("mission")),
        players=[PlayerEntryOut(**p) for p in players_raw],
        weather=WeatherInfoOut(**weather_raw) if weather_raw else None,
    )

    # Per-server stats (camelCase keys from DCSServerBot API)
    stats_data = await dcsbot_service.get_server_stats_by_name(server_name)
    stats_out = _build_stats(stats_data) if stats_data else None

    # Attendance (snake_case keys, optional)
    attendance_data = await dcsbot_service.get_server_attendance(server_name)
    attendance_out = None
    if attendance_data:
        attendance_out = DcsBotAttendanceOut(
            current_players=attendance_data.get("current_players", 0),
            unique_players_24h=attendance_data.get("unique_players_24h", 0),
            total_playtime_hours_24h=attendance_data.get("total_playtime_hours_24h", 0),
            discord_members_24h=attendance_data.get("discord_members_24h", 0),
            unique_players_7d=attendance_data.get("unique_players_7d", 0),
            total_playtime_hours_7d=attendance_data.get("total_playtime_hours_7d", 0),
            discord_members_7d=attendance_data.get("discord_members_7d", 0),
            unique_players_30d=attendance_data.get("unique_players_30d", 0),
            total_playtime_hours_30d=attendance_data.get("total_playtime_hours_30d", 0),
            discord_members_30d=attendance_data.get("discord_members_30d", 0),
            total_sorties=attendance_data.get("total_sorties"),
            total_kills=attendance_data.get("total_kills"),
            total_deaths=attendance_data.get("total_deaths"),
            total_pvp_kills=attendance_data.get("total_pvp_kills"),
            total_pvp_deaths=attendance_data.get("total_pvp_deaths"),
            top_theatres=[TopTheatreOut(**t) for t in attendance_data.get("top_theatres") or []],
            top_missions=[TopMissionOut(**m) for m in attendance_data.get("top_missions") or []],
            top_modules=[TopModuleOut(**m) for m in attendance_data.get("top_modules") or []],
        )

    return DcsBotServerDetailPageOut(server=server_out, stats=stats_out, attendance=attendance_out)
