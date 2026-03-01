from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.auth.permissions import can_add_activity, can_mark_presentation
from app.database import get_db
from app.models.recruitment import RecruitmentEvent
from app.models.user import User

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.get("/{user_id}")
async def get_recruitment_history(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RecruitmentEvent)
        .where(RecruitmentEvent.user_id == user_id)
        .options(selectinload(RecruitmentEvent.validator))
        .order_by(RecruitmentEvent.event_at.asc())
    )
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "type": e.type,
            "type_as_string": e.type_as_string,
            "event_at": e.event_at,
            "comment": e.comment,
            "validator_nickname": e.validator.nickname if e.validator else None,
            "ack_at": e.ack_at,
        }
        for e in events
    ]


@router.post("/{user_id}/events")
async def add_recruitment_event(
    user_id: int, type: int, comment: str | None = None,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    now = datetime.now(UTC)

    if type == RecruitmentEvent.TYPE_PRESENTATION:
        if not can_mark_presentation(user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        target.need_presentation = False
        target.updated_at = now

    elif type == RecruitmentEvent.TYPE_ACTIVITY:
        if not can_add_activity(user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        target.cadet_flights += 1
        target.updated_at = now

    event = RecruitmentEvent(
        user_id=user_id,
        type=type,
        validator_id=user.id,
        event_at=now,
        comment=comment,
        created_at=now,
        updated_at=now,
    )
    db.add(event)
    await db.commit()

    return {"detail": "Recruitment event created"}
