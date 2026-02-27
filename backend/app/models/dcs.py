from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Server(Base):
    __tablename__ = "server"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ucid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)
    join_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_join_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User | None"] = relationship("User", back_populates="player", uselist=False)


class DcsBotSyncState(Base):
    __tablename__ = "dcsbot_sync_state"

    server_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    records_imported: Mapped[int] = mapped_column(Integer, default=0)


from app.models.user import User  # noqa: E402, F811
