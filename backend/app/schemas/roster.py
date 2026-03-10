from pydantic import BaseModel, Field


class RosterStatsOut(BaseModel):
    all: int
    cadets: int
    members: int
    cadets_need_presentation: int = 0
    cadets_ready_to_promote: int = 0


class RosterUserOut(BaseModel):
    id: int
    nickname: str
    status: int
    status_as_string: str | None = None
    active_module_count: int = 0
    need_presentation: bool = False
    is_ready_to_promote: bool = False


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
    total_group_count: int = 0


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


class OfficeMemberOut(BaseModel):
    nickname: str
    status: int
    status_as_string: str | None = None


class OfficeOut(BaseModel):
    president: OfficeMemberOut | None = None
    president_deputy: OfficeMemberOut | None = None
    treasurer: OfficeMemberOut | None = None
    treasurer_deputy: OfficeMemberOut | None = None
    secretary: OfficeMemberOut | None = None
    secretary_deputy: OfficeMemberOut | None = None
