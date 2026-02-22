from pydantic import BaseModel


class ModuleRoleOut(BaseModel):
    id: int
    name: str
    code: str
    position: int

    model_config = {"from_attributes": True}


class ModuleSystemOut(BaseModel):
    id: int
    code: str
    name: str
    position: int

    model_config = {"from_attributes": True}


class ModuleOut(BaseModel):
    id: int
    type: int
    type_as_string: str | None = None
    name: str
    long_name: str
    code: str
    landing_page: bool
    landing_page_number: int | None = None
    period: int | None = None
    period_as_string: str | None = None
    image_uuid: str | None = None
    image_header_uuid: str | None = None
    roles: list[ModuleRoleOut] = []
    systems: list[ModuleSystemOut] = []

    model_config = {"from_attributes": True}


# --- Input schemas ---


class ModuleRoleCreate(BaseModel):
    name: str
    code: str
    position: int


class ModuleRoleUpdate(BaseModel):
    name: str
    code: str
    position: int


class ModuleSystemCreate(BaseModel):
    code: str
    name: str
    position: int = 0


class ModuleSystemUpdate(BaseModel):
    code: str
    name: str
    position: int = 0


class ModuleCreate(BaseModel):
    type: int
    name: str
    long_name: str
    code: str
    landing_page: bool = False
    landing_page_number: int | None = None
    period: int | None = None
    role_ids: list[int] = []
    system_ids: list[int] = []


class ModuleUpdate(BaseModel):
    type: int
    name: str
    long_name: str
    code: str
    landing_page: bool = False
    landing_page_number: int | None = None
    period: int | None = None
    role_ids: list[int] = []
    system_ids: list[int] = []
