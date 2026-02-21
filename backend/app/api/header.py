from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.calendar import CalendarEvent

router = APIRouter(prefix="/header", tags=["header"])


@router.get("")
async def get_header_data(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # Next upcoming events
    result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.start_date > now, CalendarEvent.deleted == False)  # noqa: E712
        .order_by(CalendarEvent.start_date)
        .limit(3)
    )
    next_events = result.scalars().all()

    return {
        "ts_client_count": 0,  # TODO: From TeamSpeak cache
        "next_events": [
            {
                "id": e.id,
                "title": e.title,
                "start_date": e.start_date,
                "type": e.type,
                "type_color": e.type_color,
            }
            for e in next_events
        ],
    }
