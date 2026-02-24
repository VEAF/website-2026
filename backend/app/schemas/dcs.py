from datetime import datetime

from pydantic import BaseModel, Field


class ServerOut(BaseModel):
    id: int
    name: str
    code: str
    atc: bool
    gci: bool

    model_config = {"from_attributes": True}


# --- DCSServerBot API response schemas ---


class MissionInfoOut(BaseModel):
    name: str
    uptime: int
    date_time: str | None = None
    theatre: str
    blue_slots: int | None = None
    blue_slots_used: int | None = None
    red_slots: int | None = None
    red_slots_used: int | None = None


class PlayerEntryOut(BaseModel):
    nick: str
    side: str | None = None
    unit_type: str | None = None
    callsign: str | None = None


class DcsBotServerOut(BaseModel):
    name: str
    status: str
    num_players: int
    mission: MissionInfoOut | None = None
    players: list[PlayerEntryOut] = Field(default_factory=list)


class DcsBotStatsOut(BaseModel):
    total_players: int
    active_players: int
    total_sorties: int
    avg_playtime: int
    total_kills: int
    total_deaths: int
    total_pvp_kills: int
    total_pvp_deaths: int


class DcsBotPageOut(BaseModel):
    servers: list[DcsBotServerOut]
    stats: DcsBotStatsOut | None = None


# --- DCSServerBot server detail schemas ---


class WeatherInfoOut(BaseModel):
    temperature: float | None = None
    wind_speed: float | None = None
    wind_direction: int | None = None
    pressure: float | None = None
    visibility: int | None = None
    clouds_base: int | None = None
    clouds_density: int | None = None
    precipitation: int | None = None
    fog_enabled: bool | None = None
    fog_visibility: int | None = None
    dust_enabled: bool | None = None
    dust_visibility: int | None = None


class DcsBotServerDetailOut(BaseModel):
    name: str
    status: str
    num_players: int
    address: str | None = None
    password: str | None = None
    restart_time: str | None = None
    mission: MissionInfoOut | None = None
    players: list[PlayerEntryOut] = Field(default_factory=list)
    weather: WeatherInfoOut | None = None


class TopTheatreOut(BaseModel):
    theatre: str
    playtime_hours: float


class TopMissionOut(BaseModel):
    mission_name: str
    playtime_hours: float


class TopModuleOut(BaseModel):
    module: str
    playtime_hours: float


class DcsBotAttendanceOut(BaseModel):
    current_players: int
    unique_players_24h: int
    total_playtime_hours_24h: float
    discord_members_24h: int
    unique_players_7d: int
    total_playtime_hours_7d: float
    discord_members_7d: int
    unique_players_30d: int
    total_playtime_hours_30d: float
    discord_members_30d: int
    total_sorties: int | None = None
    total_kills: int | None = None
    total_deaths: int | None = None
    total_pvp_kills: int | None = None
    total_pvp_deaths: int | None = None
    top_theatres: list[TopTheatreOut] = Field(default_factory=list)
    top_missions: list[TopMissionOut] = Field(default_factory=list)
    top_modules: list[TopModuleOut] = Field(default_factory=list)


class DcsBotServerDetailPageOut(BaseModel):
    server: DcsBotServerDetailOut
    stats: DcsBotStatsOut | None = None
    attendance: DcsBotAttendanceOut | None = None


# --- DB entity schemas ---


class PlayerOut(BaseModel):
    id: int
    ucid: str
    nickname: str | None = None
    join_at: datetime | None = None
    last_join_at: datetime | None = None
    user_nickname: str | None = None

    model_config = {"from_attributes": True}
