from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.calendar import CalendarEvent
from app.schemas.header import HeaderDataOut, NextEventOut
from app.services import dcsbot as dcsbot_service

router = APIRouter(prefix="/header", tags=["header"])

NEXT_EVENTS_DAYS = 7


@router.get("", response_model=HeaderDataOut)
async def get_header_data(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # Connected DCS players (from cached DCSServerBot API)
    connected_players = 0
    servers_data = await dcsbot_service.get_servers()
    if servers_data:
        for s in servers_data:
            if s.get("status") == "Running":
                connected_players += len(s.get("players") or [])

    # Count of upcoming events in the next N days
    end = now + timedelta(days=NEXT_EVENTS_DAYS)
    count_result = await db.execute(
        select(func.count())
        .select_from(CalendarEvent)
        .where(CalendarEvent.start_date > now, CalendarEvent.start_date <= end, CalendarEvent.deleted == False)  # noqa: E712
    )
    next_events_count = count_result.scalar() or 0

    # Next 3 upcoming events (detail)
    result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.start_date > now, CalendarEvent.deleted == False)  # noqa: E712
        .order_by(CalendarEvent.start_date)
        .limit(3)
    )
    next_events = result.scalars().all()

    return HeaderDataOut(
        connected_players=connected_players,
        next_events_count=next_events_count,
        ts_client_count=0,  # TODO: From TeamSpeak cache
        next_events=[
            NextEventOut(
                id=e.id,
                title=e.title,
                start_date=e.start_date,
                type=e.type,
                type_color=e.type_color,
            )
            for e in next_events
        ],
    )
