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


# --- Admin schemas ---


class PageCreate(BaseModel):
    title: str
    route: str
    path: str
    enabled: bool = False
    restriction: int = 0


class PageUpdate(BaseModel):
    title: str
    route: str
    path: str
    enabled: bool
    restriction: int


class AdminPageOut(BaseModel):
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


class AdminPageListOut(BaseModel):
    items: list[AdminPageOut]
    total: int


class PageBlockCreate(BaseModel):
    content: str
    number: int
    enabled: bool = False


class PageBlockUpdate(BaseModel):
    content: str
    number: int
    enabled: bool


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


# --- Admin Menu Item schemas ---


class AdminMenuItemOut(BaseModel):
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
    menu_id: int | None = None
    menu_label: str | None = None
    url_id: int | None = None
    url_slug: str | None = None
    page_id: int | None = None
    page_title: str | None = None

    model_config = {"from_attributes": True}


class AdminMenuItemListOut(BaseModel):
    items: list[AdminMenuItemOut]
    total: int


class AdminMenuItemTreeOut(BaseModel):
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
    menu_id: int | None = None
    url_id: int | None = None
    url_slug: str | None = None
    page_id: int | None = None
    page_title: str | None = None
    items: list["AdminMenuItemTreeOut"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MenuItemCreate(BaseModel):
    label: str | None = None
    type: int
    icon: str | None = None
    theme_classes: str | None = None
    enabled: bool = False
    position: int | None = None
    link: str | None = None
    restriction: int = 0
    menu_id: int | None = None
    url_id: int | None = None
    page_id: int | None = None


class MenuItemUpdate(BaseModel):
    label: str | None = None
    type: int
    icon: str | None = None
    theme_classes: str | None = None
    enabled: bool
    position: int | None = None
    link: str | None = None
    restriction: int
    menu_id: int | None = None
    url_id: int | None = None
    page_id: int | None = None


class MenuItemReorderEntry(BaseModel):
    id: int
    menu_id: int | None = None
    position: int


class MenuItemReorderRequest(BaseModel):
    items: list[MenuItemReorderEntry] = Field(default_factory=list)


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
    delay: int
    status: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UrlCreate(BaseModel):
    slug: str
    target: str
    delay: int = 0
    status: bool = True


class UrlUpdate(BaseModel):
    slug: str
    target: str
    delay: int
    status: bool


class AdminUrlListOut(BaseModel):
    items: list[UrlOut]
    total: int
