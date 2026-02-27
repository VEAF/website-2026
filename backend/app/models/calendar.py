from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Many-to-many: event <-> modules
event_module_table = Table(
    "event_module",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("calendar_event.id"), primary_key=True),
    Column("module_id", Integer, ForeignKey("module.id"), primary_key=True),
)


class CalendarEvent(Base):
    __tablename__ = "calendar_event"

    # Event types
    EVENT_TYPE_TRAINING = 1
    EVENT_TYPE_MISSION = 2
    EVENT_TYPE_OPEX = 3
    EVENT_TYPE_MEETING = 4
    EVENT_TYPE_MAINTENANCE = 5
    EVENT_TYPE_ATC = 6

    EVENTS = {
        EVENT_TYPE_TRAINING: "Training",
        EVENT_TYPE_MISSION: "Mission",
        EVENT_TYPE_OPEX: "OPEX",
        EVENT_TYPE_MEETING: "Meeting",
        EVENT_TYPE_MAINTENANCE: "Maintenance",
        EVENT_TYPE_ATC: "ATC / GCI",
    }

    EVENTS_COLORS = {
        EVENT_TYPE_TRAINING: "#27AE60",
        EVENT_TYPE_MISSION: "#F1C40F",
        EVENT_TYPE_OPEX: "#7D3C98",
        EVENT_TYPE_MEETING: "#2980B9",
        EVENT_TYPE_MAINTENANCE: "#E74C3C",
        EVENT_TYPE_ATC: "#EA9417",
    }

    # Repeat types
    REPEAT_NONE = 0
    REPEAT_DAY_OF_WEEK = 1
    REPEAT_DAY_OF_MONTH = 2
    REPEAT_NTH_WEEK_DAY_OF_MONTH = 3

    REPEATS = {
        REPEAT_NONE: "Pas de répétition",
        REPEAT_DAY_OF_WEEK: "1x par semaine, le même jour",
        REPEAT_DAY_OF_MONTH: "1x par mois, le même jour",
        REPEAT_NTH_WEEK_DAY_OF_MONTH: "1x par mois, même jour de la semaine",
    }

    # Restrictions
    RESTRICTION_CADET = 1
    RESTRICTION_MEMBER = 2

    RESTRICTIONS = {
        RESTRICTION_CADET: "Cadets",
        RESTRICTION_MEMBER: "Membres",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    sim_dcs: Mapped[bool] = mapped_column(Boolean, default=False)
    sim_bms: Mapped[bool] = mapped_column(Boolean, default=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    restrictions: Mapped[str | None] = mapped_column(String(255), nullable=True)  # comma-separated
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registration: Mapped[bool] = mapped_column(Boolean, default=False)
    ato: Mapped[bool] = mapped_column(Boolean, default=False)
    debrief: Mapped[str | None] = mapped_column(Text, nullable=True)
    repeat_event: Mapped[int] = mapped_column(Integer, default=REPEAT_NONE)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    map_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("module.id"), nullable=True)
    image_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("file.id"), nullable=True)
    server_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("server.id"), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])
    map: Mapped["Module | None"] = relationship("Module", foreign_keys=[map_id])
    image: Mapped["File | None"] = relationship("File", foreign_keys=[image_id])
    server: Mapped["Server | None"] = relationship("Server", foreign_keys=[server_id])
    modules: Mapped[list["Module"]] = relationship("Module", secondary=event_module_table)
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="event", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="event", cascade="all, delete-orphan")
    choices: Mapped[list["Choice"]] = relationship("Choice", back_populates="event", cascade="all, delete-orphan")
    flights: Mapped[list["Flight"]] = relationship("Flight", back_populates="event", cascade="all, delete-orphan", order_by="Flight.name")

    @property
    def type_as_string(self) -> str:
        return self.EVENTS.get(self.type, "inconnu")

    @property
    def type_color(self) -> str:
        return self.EVENTS_COLORS.get(self.type, "#000000")

    @property
    def is_finished(self) -> bool:
        return self.end_date < datetime.now(UTC)

    def has_restriction(self, restriction: int) -> bool:
        if not self.restrictions:
            return False
        return str(restriction) in self.restrictions.split(",")

    def get_restrictions_list(self) -> list[int]:
        if not self.restrictions:
            return []
        return [int(r) for r in self.restrictions.split(",") if r.strip()]


class Flight(Base):
    __tablename__ = "flight"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    mission: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nb_slots: Mapped[int] = mapped_column(Integer, nullable=False)

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("calendar_event.id"), nullable=False)
    aircraft_id: Mapped[int] = mapped_column(Integer, ForeignKey("module.id"), nullable=False)

    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="flights")
    aircraft: Mapped["Module"] = relationship("Module", foreign_keys=[aircraft_id])
    slots: Mapped[list["Slot"]] = relationship("Slot", back_populates="flight", cascade="all, delete-orphan")


class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    flight_id: Mapped[int] = mapped_column(Integer, ForeignKey("flight.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    flight: Mapped["Flight"] = relationship("Flight", back_populates="slots")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])


class Choice(Base):
    __tablename__ = "event_choice"

    TASK_UNDEFINED = 0
    TASK_CAP = 1
    TASK_CAS = 2
    TASK_SEAD = 3
    TASK_ESCORT = 4
    TASK_TRANSPORT = 5

    TASKS = {
        TASK_UNDEFINED: "non définie",
        TASK_CAP: "CAP",
        TASK_CAS: "CAS / Strike",
        TASK_SEAD: "SEAD",
        TASK_ESCORT: "Escorte",
        TASK_TRANSPORT: "Transport",
    }

    TASK_ICONS = {
        TASK_UNDEFINED: "fa-solid fa-question",
        TASK_CAP: "fa-solid fa-shield-halved",
        TASK_CAS: "fa-solid fa-crosshairs",
        TASK_SEAD: "fa-solid fa-bolt",
        TASK_ESCORT: "fa-solid fa-jet-fighter",
        TASK_TRANSPORT: "fa-solid fa-truck-plane",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("calendar_event.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("module.id"), nullable=False)

    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="choices")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    module: Mapped["Module"] = relationship("Module", foreign_keys=[module_id])

    @property
    def task_as_string(self) -> str:
        return self.TASKS.get(self.task, "non définie")


class Vote(Base):
    __tablename__ = "event_vote"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    vote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # True=yes, False=no, None=maybe
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Deprecated: no longer used in the UI

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("calendar_event.id"), nullable=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="votes")


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("calendar_event.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="notifications")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


from app.models.user import User  # noqa: E402, F811
from app.models.module import Module  # noqa: E402, F811
from app.models.content import File  # noqa: E402, F811
from app.models.dcs import Server  # noqa: E402, F811
