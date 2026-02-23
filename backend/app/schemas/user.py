from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


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
    roles: list[str] = Field(default_factory=list)
    need_presentation: bool
    cadet_flights: int
    modules: list[UserModuleOut] = Field(default_factory=list)


class UserUpdate(BaseModel):
    discord: str | None = None
    forum: str | None = None
    sim_dcs: bool | None = None
    sim_bms: bool | None = None


# --- Profile module update schemas ---


class UserModuleLevelUpdate(BaseModel):
    level: int = Field(ge=0, le=3)


class UserModuleActiveUpdate(BaseModel):
    active: bool


class UserModuleUpdateResponse(BaseModel):
    module_id: int
    active: bool
    level: int
    level_as_string: str | None = None
    deleted: bool = False


# --- Admin schemas ---


class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    roles: list[str] = Field(default_factory=list)
    status: int
    status_as_string: str | None = None
    sim_dcs: bool
    sim_bms: bool
    discord: str | None = None
    forum: str | None = None
    need_presentation: bool
    cadet_flights: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    email: EmailStr
    nickname: str
    roles: list[str] = Field(default_factory=list)
    status: int
    discord: str | None = None
    forum: str | None = None
    sim_dcs: bool = False
    sim_bms: bool = False
    need_presentation: bool = False


class AdminUserListOut(BaseModel):
    items: list[AdminUserOut]
    total: int
