from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecruitmentEvent(Base):
    __tablename__ = "recruitment_event"

    TYPE_TO_APPLY = 1
    TYPE_PRESENTATION = 2
    TYPE_PROMOTE = 3
    TYPE_ACTIVITY = 4
    TYPE_GUEST = 5

    TYPES = {
        TYPE_TO_APPLY: "candidature",
        TYPE_PRESENTATION: "presentation",
        TYPE_PROMOTE: "promotion",
        TYPE_ACTIVITY: "activité",
        TYPE_GUEST: "invité",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    ack_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    validator_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="recruitment_events", foreign_keys=[user_id])
    validator: Mapped["User | None"] = relationship("User", foreign_keys=[validator_id])

    @property
    def type_as_string(self) -> str:
        return self.TYPES.get(self.type, "inconnu")


from app.models.user import User  # noqa: E402, F811
