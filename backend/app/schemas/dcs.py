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


# --- DB entity schemas ---


class PlayerOut(BaseModel):
    id: int
    ucid: str
    nickname: str | None = None
    join_at: datetime | None = None
    last_join_at: datetime | None = None
    user_nickname: str | None = None

    model_config = {"from_attributes": True}
