"""Service for recurring calendar event management."""

import calendar as cal
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.calendar import CalendarEvent

logger = logging.getLogger(__name__)

AUTO_CREATE_EVENT_DAYS = 32


def get_next_event_datetime(event: CalendarEvent) -> datetime | None:
    """Calculate the next occurrence datetime based on the event's repeat type."""
    start = event.start_date

    if event.repeat_event == CalendarEvent.REPEAT_DAY_OF_WEEK:
        return start + timedelta(weeks=1)

    if event.repeat_event == CalendarEvent.REPEAT_DAY_OF_MONTH:
        year = start.year
        month = start.month + 1
        if month > 12:
            month = 1
            year += 1
        max_day = cal.monthrange(year, month)[1]
        day = min(start.day, max_day)
        return start.replace(year=year, month=month, day=day)

    if event.repeat_event == CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH:
        nth = (start.day - 1) // 7
        weekday = start.weekday()  # 0=Monday ... 6=Sunday

        year = start.year
        month = start.month + 1
        if month > 12:
            month = 1
            year += 1

        month_cal = cal.monthcalendar(year, month)
        occurrences = [week[weekday] for week in month_cal if week[weekday] != 0]

        if nth >= len(occurrences):
            target_day = occurrences[-1]
        else:
            target_day = occurrences[nth]

        return start.replace(year=year, month=month, day=target_day)

    return None


def is_needed_to_create_next_event(event: CalendarEvent) -> bool:
    """Check if the next occurrence should be created (within 32 days from now)."""
    next_date = get_next_event_datetime(event)
    if next_date is None:
        return False
    now = datetime.now(UTC)
    # Handle timezone-naive datetimes (e.g. from SQLite in tests)
    if next_date.tzinfo is None:
        now = now.replace(tzinfo=None)
    delta = next_date - now
    return delta.days <= AUTO_CREATE_EVENT_DAYS


async def create_next_event(db: AsyncSession, original: CalendarEvent) -> CalendarEvent:
    """Create the next recurring event from the original.

    Clones all event properties except debrief, votes, choices, flights, notifications.
    The new event inherits repeat_event; the original is set to REPEAT_NONE.
    Expects original.modules to be eagerly loaded (via selectinload).
    """
    next_start = get_next_event_datetime(original)
    if next_start is None:
        raise ValueError("Cannot calculate next event date")

    duration = original.end_date - original.start_date
    now = datetime.now(UTC)

    new_event = CalendarEvent(
        title=original.title,
        start_date=next_start,
        end_date=next_start + duration,
        type=original.type,
        sim_dcs=original.sim_dcs,
        sim_bms=original.sim_bms,
        description=original.description,
        restrictions=original.restrictions,
        registration=original.registration,
        ato=original.ato,
        repeat_event=original.repeat_event,
        map_id=original.map_id,
        server_id=original.server_id,
        image_id=original.image_id,
        owner_id=original.owner_id,
        debrief=None,
        created_at=now,
        updated_at=now,
    )
    # Eagerly load modules via explicit query to avoid lazy-load issues
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == original.id).options(selectinload(CalendarEvent.modules))
    )
    loaded = result.scalar_one()
    for m in loaded.modules:
        new_event.modules.append(m)

    db.add(new_event)
    await db.flush()

    original.repeat_event = CalendarEvent.REPEAT_NONE
    original.updated_at = now

    return new_event


async def check_recurring_events(db: AsyncSession) -> int:
    """Find all repeatable events and create next occurrences as needed.

    Returns the number of new events created.
    """
    query = (
        select(CalendarEvent)
        .where(
            CalendarEvent.deleted == False,  # noqa: E712
            CalendarEvent.repeat_event != CalendarEvent.REPEAT_NONE,
        )
        .options(selectinload(CalendarEvent.modules))
    )
    result = await db.execute(query)
    events = result.scalars().all()

    count = 0
    for event in events:
        if is_needed_to_create_next_event(event):
            logger.info("Creating next event from id=%d '%s' (repeat=%d)", event.id, event.title, event.repeat_event)
            new_event = await create_next_event(db, event)
            logger.info("New event created: id=%d '%s' (repeat=%d)", new_event.id, new_event.title, new_event.repeat_event)
            count += 1

    await db.commit()
    return count
