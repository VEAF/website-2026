"""Integration tests for recurring calendar events processing."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar import CalendarEvent
from app.services.calendar import check_recurring_events, create_next_event
from tests.factories import EventFactory, UserFactory


async def _create_user(db: AsyncSession):
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_event(db: AsyncSession, owner_id: int, **kwargs) -> CalendarEvent:
    event = EventFactory.build(owner_id=owner_id, **kwargs)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@pytest.mark.asyncio
async def test_check_recurring_creates_weekly_event(db_session: AsyncSession):
    # GIVEN a weekly repeating event starting in 3 days
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    event = await _create_event(
        db_session,
        owner_id=user.id,
        title="Weekly Training",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, hours=2),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
    )
    original_id = event.id

    # WHEN
    count = await check_recurring_events(db_session)

    # THEN one new event was created
    assert count == 1

    # AND the original event no longer repeats
    await db_session.refresh(event)
    assert event.repeat_event == CalendarEvent.REPEAT_NONE

    # AND the new event exists with correct data
    result = await db_session.execute(
        select(CalendarEvent).where(
            CalendarEvent.id != original_id,
            CalendarEvent.title == "Weekly Training",
        )
    )
    new_event = result.scalar_one()
    assert new_event.repeat_event == CalendarEvent.REPEAT_DAY_OF_WEEK
    assert new_event.debrief is None
    assert new_event.owner_id == user.id


@pytest.mark.asyncio
async def test_check_recurring_skips_distant_events(db_session: AsyncSession):
    # GIVEN a weekly repeating event starting in 40 days (next = 47 > 32)
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    await _create_event(
        db_session,
        owner_id=user.id,
        title="Far Away",
        start_date=now + timedelta(days=40),
        end_date=now + timedelta(days=40, hours=2),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
    )

    # WHEN
    count = await check_recurring_events(db_session)

    # THEN
    assert count == 0


@pytest.mark.asyncio
async def test_check_recurring_skips_deleted_events(db_session: AsyncSession):
    # GIVEN a deleted repeating event within threshold
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    await _create_event(
        db_session,
        owner_id=user.id,
        title="Deleted",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, hours=2),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
        deleted=True,
    )

    # WHEN
    count = await check_recurring_events(db_session)

    # THEN
    assert count == 0


@pytest.mark.asyncio
async def test_create_next_event_preserves_duration(db_session: AsyncSession):
    # GIVEN an event with a 3-hour duration
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    event = await _create_event(
        db_session,
        owner_id=user.id,
        title="Duration Test",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, hours=3),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
    )

    # WHEN
    new_event = await create_next_event(db_session, event)

    # THEN
    duration = new_event.end_date - new_event.start_date
    assert duration == timedelta(hours=3)


@pytest.mark.asyncio
async def test_create_next_event_clears_debrief(db_session: AsyncSession):
    # GIVEN an event with a debrief
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    event = await _create_event(
        db_session,
        owner_id=user.id,
        title="With Debrief",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, hours=2),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
        debrief="Previous debrief notes",
    )

    # WHEN
    new_event = await create_next_event(db_session, event)

    # THEN
    assert new_event.debrief is None


@pytest.mark.asyncio
async def test_check_recurring_does_not_duplicate(db_session: AsyncSession):
    # GIVEN a repeating event processed once
    user = await _create_user(db_session)
    now = datetime.now(UTC)
    await _create_event(
        db_session,
        owner_id=user.id,
        title="No Duplicate",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, hours=2),
        repeat_event=CalendarEvent.REPEAT_DAY_OF_WEEK,
    )

    # WHEN run twice
    count1 = await check_recurring_events(db_session)
    count2 = await check_recurring_events(db_session)

    # THEN first run creates 1, second run creates 1 (the new event also repeats,
    # but the original no longer does — so still 1 total new event per run from the chain)
    assert count1 == 1
    assert count2 == 1

    # AND total events should be 3 (original + 2 new)
    result = await db_session.execute(
        select(CalendarEvent).where(CalendarEvent.title == "No Duplicate")
    )
    all_events = result.scalars().all()
    assert len(all_events) == 3
