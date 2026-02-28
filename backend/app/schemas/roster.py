from pydantic import BaseModel, Field


class RosterStatsOut(BaseModel):
    all: int
    cadets: int
    members: int


class RosterUserModuleOut(BaseModel):
    module_id: int
    module_name: str | None = None
    module_code: str | None = None
    module_long_name: str | None = None
    module_type: int | None = None
    module_type_as_string: str | None = None
    module_period: int | None = None
    module_period_as_string: str | None = None
    active: bool
    level: int
    level_as_string: str | None = None


class RosterUserOut(BaseModel):
    id: int
    nickname: str
    status: int
    status_as_string: str | None = None
    sim_dcs: bool
    sim_bms: bool
    modules: list[RosterUserModuleOut] = Field(default_factory=list)


class RosterModuleOut(BaseModel):
    id: int
    name: str
    long_name: str
    code: str
    type: int
    period: int | None = None
    period_as_string: str | None = None
    image_header_uuid: str | None = None
    user_count: int = 0


class RosterModuleDetailUserOut(BaseModel):
    id: int
    nickname: str
    status: int
    status_as_string: str | None = None
    active: bool
    level: int
    level_as_string: str | None = None


class RosterModuleDetailOut(BaseModel):
    module: RosterModuleOut
    users: list[RosterModuleDetailUserOut] = Field(default_factory=list)
