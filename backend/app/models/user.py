from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email", name="email_idx"),
        UniqueConstraint("nickname", name="nickname_idx"),
    )

    # Status constants
    STATUS_UNKNOWN = 0
    STATUS_CADET = 1
    STATUS_MEMBER = 2
    STATUS_SECRETARY_DEPUTY = 3
    STATUS_SECRETARY = 4
    STATUS_TREASURER_DEPUTY = 5
    STATUS_TREASURER = 6
    STATUS_PRESIDENT_DEPUTY = 7
    STATUS_PRESIDENT = 8
    STATUS_GUEST = 9

    STATUSES = {
        STATUS_UNKNOWN: "inconnu",
        STATUS_CADET: "cadet",
        STATUS_MEMBER: "membre",
        STATUS_SECRETARY_DEPUTY: "secrétaire adjoint",
        STATUS_SECRETARY: "secrétaire",
        STATUS_TREASURER_DEPUTY: "trésorier adjoint",
        STATUS_TREASURER: "trésorier",
        STATUS_PRESIDENT_DEPUTY: "président adjoint",
        STATUS_PRESIDENT: "président",
        STATUS_GUEST: "invité",
    }

    STATUSES_GUEST = [STATUS_UNKNOWN, STATUS_GUEST]
    STATUSES_MEMBER = [
        STATUS_MEMBER, STATUS_SECRETARY_DEPUTY, STATUS_SECRETARY,
        STATUS_TREASURER_DEPUTY, STATUS_TREASURER,
        STATUS_PRESIDENT_DEPUTY, STATUS_PRESIDENT,
    ]
    STATUSES_OFFICE = [
        STATUS_SECRETARY_DEPUTY, STATUS_SECRETARY,
        STATUS_TREASURER_DEPUTY, STATUS_TREASURER,
        STATUS_PRESIDENT_DEPUTY, STATUS_PRESIDENT,
    ]

    CADET_MIN_FLIGHTS = 5

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    roles: Mapped[str] = mapped_column(String(255), nullable=False, default="")  # comma-separated
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    password_request_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_request_expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    sim_bms: Mapped[bool] = mapped_column(Boolean, default=False)
    sim_dcs: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[int] = mapped_column(Integer, default=STATUS_UNKNOWN)
    need_presentation: Mapped[bool] = mapped_column(Boolean, default=False)
    cadet_flights: Mapped[int] = mapped_column(Integer, default=0)
    discord: Mapped[str | None] = mapped_column(String(64), nullable=True)
    forum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("player.id"), nullable=True)
    player: Mapped["Player | None"] = relationship("Player", back_populates="user", foreign_keys=[player_id])

    modules: Mapped[list["UserModule"]] = relationship("UserModule", back_populates="user", cascade="all, delete-orphan")
    files: Mapped[list["File"]] = relationship("File", back_populates="owner")
    recruitment_events: Mapped[list["RecruitmentEvent"]] = relationship("RecruitmentEvent", back_populates="user", foreign_keys="RecruitmentEvent.user_id")

    def get_roles_list(self) -> list[str]:
        roles = [r.strip() for r in self.roles.split(",") if r.strip()] if self.roles else []
        if "ROLE_USER" not in roles:
            roles.append("ROLE_USER")
        return roles

    def has_role(self, role: str) -> bool:
        return role in self.get_roles_list()

    @property
    def is_guest(self) -> bool:
        return self.status in self.STATUSES_GUEST

    @property
    def is_member(self) -> bool:
        return self.status in self.STATUSES_MEMBER

    @property
    def is_cadet(self) -> bool:
        return self.status == self.STATUS_CADET

    @property
    def is_office(self) -> bool:
        return self.status in self.STATUSES_OFFICE

    @property
    def is_admin(self) -> bool:
        return self.has_role("ROLE_ADMIN")

    @property
    def status_as_string(self) -> str:
        return self.STATUSES.get(self.status, "inconnu")

    @property
    def recruitment_status(self) -> str:
        if self.status == self.STATUS_CADET:
            return "cadet"
        if self.status == self.STATUS_GUEST:
            return "guest"
        if self.status in self.STATUSES_MEMBER:
            return "member"
        return "unknown"


class UserModule(Base):
    __tablename__ = "user_module"
    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="usermodule_idx"),
    )

    LEVEL_UNKNOWN = 0
    LEVEL_ROOKIE = 1
    LEVEL_MISSION = 2
    LEVEL_INSTRUCTOR = 3

    LEVELS = {
        LEVEL_UNKNOWN: "inconnu",
        LEVEL_ROOKIE: "débutant",
        LEVEL_MISSION: "mission",
        LEVEL_INSTRUCTOR: "instructeur",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("module.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    level: Mapped[int] = mapped_column(Integer, default=LEVEL_UNKNOWN)

    user: Mapped["User"] = relationship("User", back_populates="modules")
    module: Mapped["Module"] = relationship("Module", back_populates="users")

    @property
    def level_as_string(self) -> str:
        return self.LEVELS.get(self.level, "inconnu")


# Forward references for type checking
from app.models.dcs import Player  # noqa: E402, F811
from app.models.content import File  # noqa: E402, F811
from app.models.recruitment import RecruitmentEvent  # noqa: E402, F811
from app.models.module import Module  # noqa: E402, F811
