from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserModuleOut(BaseModel):
    id: int
    module_id: int
    module_name: str | None = None
    module_code: str | None = None
    module_long_name: str | None = None
    module_type: int | None = None
    active: bool
    level: int
    level_as_string: str | None = None

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    id: int
    nickname: str
    status: int
    status_as_string: str | None = None
    sim_dcs: bool
    sim_bms: bool
    discord: str | None = None
    forum: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserMe(UserPublic):
    email: EmailStr
    roles: list[str] = []
    need_presentation: bool
    cadet_flights: int
    modules: list[UserModuleOut] = []


class UserUpdate(BaseModel):
    nickname: str | None = None
    discord: str | None = None
    forum: str | None = None
    sim_dcs: bool | None = None
    sim_bms: bool | None = None
