from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class ServerOut(BaseModel):
    id: int
    name: str
    code: str
    dcsbot_name: str | None = None
    sitac_url: str | None = None

    model_config = {"from_attributes": True}


class ServerCreate(BaseModel):
    name: str
    code: str
    dcsbot_name: str | None = None
    sitac_url: str | None = None

    @field_validator("dcsbot_name", "sitac_url", mode="before")
    @classmethod
    def _blank_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            value = value.strip()
        return value or None

    @field_validator("sitac_url")
    @classmethod
    def _http_url_only(cls, value: str | None) -> str | None:
        # Rendered as a link: only web addresses, never javascript: or data: URLs
        if value is not None and urlparse(value).scheme not in ("http", "https"):
            raise ValueError("L'URL de la SITAC doit commencer par http:// ou https://")
        return value


class ServerUpdate(ServerCreate):
    pass


class AdminServerListOut(BaseModel):
    items: list[ServerOut]
    total: int


# --- DCSServerBot API response schemas ---


class SunStateOut(BaseModel):
    state: str  # day|night|dawn|dusk
    icon: str  # FontAwesome CSS class
    color: str  # hex color
    tooltip: str  # French label


class MissionInfoOut(BaseModel):
    name: str
    uptime: int
    date_time: str | None = None
    theatre: str
    blue_slots: int | None = None
    blue_slots_used: int | None = None
    red_slots: int | None = None
    red_slots_used: int | None = None
    sun_state: SunStateOut | None = None
    mission_time: str | None = None  # "HH:MM"
    mission_date_time: str | None = None  # "DD/MM/YYYY HH:MM"


class PlayerEntryOut(BaseModel):
    nick: str
    side: str | None = None
    unit_type: str | None = None
    callsign: str | None = None


class DcsBotServerOut(BaseModel):
    name: str
    status: str
    num_players: int
    sitac_url: str | None = None
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
    sitac_url: str | None = None
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
    user_id: int | None = None
    user_nickname: str | None = None

    model_config = {"from_attributes": True}


class PlayerCreate(BaseModel):
    ucid: str
    nickname: str | None = None
    user_id: int | None = None


class PlayerUpdate(BaseModel):
    ucid: str
    nickname: str | None = None
    user_id: int | None = None


class AdminPlayerListOut(BaseModel):
    items: list[PlayerOut]
    total: int


# --- Player game statistics (user profile) ---


class DcsPlayerModuleKillsOut(BaseModel):
    module: str
    kills: int | None = None


class DcsPlayerStatsOut(BaseModel):
    playtime: int = 0
    kills: int = 0
    deaths: int = 0
    kdr: float = 0
    kills_pvp: int = 0
    deaths_pvp: int = 0
    kills_planes: int = 0
    kills_helicopters: int = 0
    kills_ships: int = 0
    kills_sams: int = 0
    kills_ground: int = 0
    takeoffs: int = 0
    landings: int = 0
    ejections: int = 0
    crashes: int = 0
    teamkills: int = 0
    kills_by_module: list[DcsPlayerModuleKillsOut] = Field(default_factory=list)


class UserDcsStatsOut(BaseModel):
    has_player: bool
    stats: DcsPlayerStatsOut | None = None
