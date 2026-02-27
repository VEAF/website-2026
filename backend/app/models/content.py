from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    __tablename__ = "file"

    TYPE_UNKNOWN = 0
    TYPE_IMAGE = 1
    TYPE_PDF = 2

    TYPES = {
        TYPE_UNKNOWN: "inconnu",
        TYPE_IMAGE: "image",
        TYPE_PDF: "pdf",
    }

    MIME_TYPES = {
        "application/pdf": TYPE_PDF,
        "image/jpg": TYPE_IMAGE,
        "image/jpeg": TYPE_IMAGE,
        "image/png": TYPE_IMAGE,
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    type: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extension: Mapped[str] = mapped_column(String(255), nullable=False)

    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    owner: Mapped["User | None"] = relationship("User", back_populates="files")

    @property
    def type_as_string(self) -> str:
        return self.TYPES.get(self.type, "inconnu")

    @property
    def is_image(self) -> bool:
        return self.type == self.TYPE_IMAGE

    @classmethod
    def type_from_mime(cls, mime_type: str) -> int:
        return cls.MIME_TYPES.get(mime_type, cls.TYPE_UNKNOWN)


class Page(Base):
    __tablename__ = "page"

    # Restriction levels
    LEVEL_ALL = 0
    LEVEL_GUEST = 1
    LEVEL_CADET = 2
    LEVEL_MEMBER = 3

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    restriction: Mapped[int] = mapped_column(Integer, default=LEVEL_ALL)

    blocks: Mapped[list["PageBlock"]] = relationship("PageBlock", back_populates="page", cascade="all, delete-orphan", order_by="PageBlock.number")


class PageBlock(Base):
    __tablename__ = "page_block"

    TYPE_NONE = 0
    TYPE_MARKDOWN = 1

    TYPES = {
        TYPE_NONE: "aucun",
        TYPE_MARKDOWN: "markdown",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    page_id: Mapped[int] = mapped_column(Integer, ForeignKey("page.id"), nullable=False)
    page: Mapped["Page"] = relationship("Page", back_populates="blocks")


class Url(Base):
    __tablename__ = "url"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    delay: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    status: Mapped[bool] = mapped_column(Boolean, default=True)


class MenuItem(Base):
    __tablename__ = "menu_item"

    TYPE_NONE = 0
    TYPE_MENU = 1
    TYPE_LINK = 2
    TYPE_URL = 3
    TYPE_PAGE = 4
    TYPE_DIVIDER = 5
    TYPE_OFFICE = 6
    TYPE_SERVERS = 7
    TYPE_ROSTER = 8
    TYPE_CALENDAR = 9
    TYPE_MISSION_MAKER = 10
    TYPE_TEAMSPEAK = 11

    TYPES = {
        TYPE_MENU: "Menu",
        TYPE_LINK: "Url personnalisée",
        TYPE_URL: "Url (redirection)",
        TYPE_PAGE: "Page",
        TYPE_DIVIDER: "Séparateur",
        TYPE_OFFICE: "Bureau",
        TYPE_SERVERS: "Serveurs",
        TYPE_ROSTER: "Roster",
        TYPE_CALENDAR: "Calendrier",
        TYPE_MISSION_MAKER: "Mission Maker",
        TYPE_TEAMSPEAK: "Team Speak",
    }

    # Restriction levels
    LEVEL_ALL = 0
    LEVEL_GUEST = 1
    LEVEL_CADET = 2
    LEVEL_MEMBER = 3

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    theme_classes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    restriction: Mapped[int] = mapped_column(Integer, default=LEVEL_ALL)

    # Self-referential for hierarchical menus
    menu_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("menu_item.id"), nullable=True)
    menu: Mapped["MenuItem | None"] = relationship("MenuItem", remote_side="MenuItem.id", back_populates="items")
    items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="menu", order_by="MenuItem.position")

    # Optional references
    url_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("url.id"), nullable=True)
    page_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("page.id"), nullable=True)
    url: Mapped["Url | None"] = relationship("Url", foreign_keys=[url_id])
    page: Mapped["Page | None"] = relationship("Page", foreign_keys=[page_id])

    @property
    def type_as_string(self) -> str:
        return self.TYPES.get(self.type, "inconnu")


from app.models.user import User  # noqa: E402, F811
