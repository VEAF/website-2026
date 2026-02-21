from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Many-to-many association tables
module_role_table = Table(
    "module_module_role",
    Base.metadata,
    Column("module_id", Integer, ForeignKey("module.id"), primary_key=True),
    Column("module_role_id", Integer, ForeignKey("module_role.id"), primary_key=True),
)

module_system_table = Table(
    "module_module_system",
    Base.metadata,
    Column("module_id", Integer, ForeignKey("module.id"), primary_key=True),
    Column("module_system_id", Integer, ForeignKey("module_system.id"), primary_key=True),
)


class Module(Base):
    __tablename__ = "module"

    TYPE_NONE = 0
    TYPE_MAP = 1
    TYPE_AIRCRAFT = 2
    TYPE_HELICOPTER = 3
    TYPE_SPECIAL = 4

    TYPES = {
        TYPE_MAP: "Carte",
        TYPE_AIRCRAFT: "Avion",
        TYPE_HELICOPTER: "Hélicoptère",
        TYPE_SPECIAL: "Spécial",
    }

    TYPES_WITH_LEVEL = [TYPE_AIRCRAFT, TYPE_HELICOPTER, TYPE_SPECIAL]

    PERIOD_NONE = 0
    PERIOD_WW2 = 1
    PERIOD_COLD_WAR = 2
    PERIOD_MODERN = 3

    PERIODS = {
        PERIOD_NONE: "",
        PERIOD_WW2: "WW2",
        PERIOD_COLD_WAR: "COLD WAR",
        PERIOD_MODERN: "MODERN",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    long_name: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    landing_page: Mapped[bool] = mapped_column(Boolean, default=False)
    landing_page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # File relationships
    image_header_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("file.id"), nullable=True)
    image_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("file.id"), nullable=True)
    image_header: Mapped["File | None"] = relationship("File", foreign_keys=[image_header_id])
    image: Mapped["File | None"] = relationship("File", foreign_keys=[image_id])

    # Relationships
    users: Mapped[list["UserModule"]] = relationship("UserModule", back_populates="module", cascade="all, delete-orphan")
    roles: Mapped[list["ModuleRole"]] = relationship("ModuleRole", secondary=module_role_table, back_populates="modules", order_by="ModuleRole.position")
    systems: Mapped[list["ModuleSystem"]] = relationship("ModuleSystem", secondary=module_system_table, back_populates="modules", order_by="ModuleSystem.position")

    @property
    def type_as_string(self) -> str:
        return self.TYPES.get(self.type, "inconnu")

    @property
    def is_with_level(self) -> bool:
        return self.type in self.TYPES_WITH_LEVEL

    @property
    def period_as_string(self) -> str:
        if self.period is None:
            return ""
        return self.PERIODS.get(self.period, "")


class ModuleRole(Base):
    __tablename__ = "module_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    modules: Mapped[list["Module"]] = relationship("Module", secondary=module_role_table, back_populates="roles")


class ModuleSystem(Base):
    __tablename__ = "module_system"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    modules: Mapped[list["Module"]] = relationship("Module", secondary=module_system_table, back_populates="systems")


from app.models.user import UserModule  # noqa: E402, F811
from app.models.content import File  # noqa: E402, F811
