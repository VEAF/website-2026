from datetime import datetime

from pydantic import BaseModel, Field


class PageBlockOut(BaseModel):
    id: int
    type: int
    content: str
    number: int
    enabled: bool

    model_config = {"from_attributes": True}


class PageOut(BaseModel):
    id: int
    route: str
    path: str
    title: str
    enabled: bool
    restriction: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    blocks: list[PageBlockOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MenuItemOut(BaseModel):
    id: int
    label: str | None = None
    type: int
    type_as_string: str | None = None
    icon: str | None = None
    theme_classes: str | None = None
    enabled: bool
    position: int | None = None
    link: str | None = None
    restriction: int
    url_slug: str | None = None
    page_path: str | None = None
    items: list["MenuItemOut"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class FileOut(BaseModel):
    id: int
    uuid: str
    type: int
    type_as_string: str | None = None
    mime_type: str
    size: int
    original_name: str | None = None
    description: str | None = None
    extension: str
    created_at: datetime | None = None
    owner_nickname: str | None = None

    model_config = {"from_attributes": True}


class UrlOut(BaseModel):
    id: int
    slug: str
    target: str
    status: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
