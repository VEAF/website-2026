from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.auth.permissions import can_add_event, can_choose_event, can_delete_event, can_edit_event, can_vote_event
from app.database import get_db
from app.models.calendar import CalendarEvent, Choice, Flight, Notification, Slot, Vote
from app.models.user import User
from app.schemas.calendar import (
    ChoiceCreate,
    ChoiceOut,
    ChoiceUpdate,
    EventCreate,
    EventDetailOut,
    EventListOut,
    EventUpdate,
    FlightOut,
    SlotOut,
    VoteCreate,
    VoteOut,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/events", response_model=list[EventListOut])
async def list_events(month: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(CalendarEvent).where(CalendarEvent.deleted == False)  # noqa: E712

    if month:
        try:
            year, m = month.split("-")
            from calendar import monthrange

            start = datetime(int(year), int(m), 1)
            _, last_day = monthrange(int(year), int(m))
            end = datetime(int(year), int(m), last_day, 23, 59, 59)
            query = query.where(and_(CalendarEvent.start_date <= end, CalendarEvent.end_date >= start))
        except ValueError:
            pass

    query = query.options(selectinload(CalendarEvent.owner)).order_by(CalendarEvent.start_date)
    result = await db.execute(query)
    events = result.scalars().all()

    return [
        EventListOut(
            id=e.id,
            title=e.title,
            start_date=e.start_date,
            end_date=e.end_date,
            type=e.type,
            type_as_string=e.type_as_string,
            type_color=e.type_color,
            sim_dcs=e.sim_dcs,
            sim_bms=e.sim_bms,
            registration=e.registration,
            owner_nickname=e.owner.nickname if e.owner else None,
        )
        for e in events
    ]


@router.get("/events/{event_id}", response_model=EventDetailOut)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.id == event_id)
        .options(
            selectinload(CalendarEvent.owner),
            selectinload(CalendarEvent.votes).selectinload(Vote.user),
            selectinload(CalendarEvent.choices).selectinload(Choice.user),
            selectinload(CalendarEvent.choices).selectinload(Choice.module),
            selectinload(CalendarEvent.flights).selectinload(Flight.aircraft),
            selectinload(CalendarEvent.flights).selectinload(Flight.slots).selectinload(Slot.user),
            selectinload(CalendarEvent.modules),
            selectinload(CalendarEvent.map),
            selectinload(CalendarEvent.image),
        )
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return EventDetailOut(
        id=event.id,
        title=event.title,
        start_date=event.start_date,
        end_date=event.end_date,
        type=event.type,
        type_as_string=event.type_as_string,
        type_color=event.type_color,
        sim_dcs=event.sim_dcs,
        sim_bms=event.sim_bms,
        registration=event.registration,
        owner_nickname=event.owner.nickname,
        description=event.description,
        restrictions=event.get_restrictions_list(),
        ato=event.ato,
        debrief=event.debrief,
        repeat_event=event.repeat_event,
        deleted=event.deleted,
        map_id=event.map_id,
        map_name=event.map.name if event.map else None,
        server_id=event.server_id,
        image_uuid=event.image.uuid if event.image else None,
        owner_id=event.owner_id,
        module_ids=[m.id for m in event.modules],
        votes=[
            VoteOut(
                id=v.id, user_id=v.user_id, user_nickname=v.user.nickname,
                vote=v.vote, comment=v.comment, created_at=v.created_at,
            )
            for v in event.votes
        ],
        choices=[
            ChoiceOut(
                id=c.id, user_id=c.user_id, user_nickname=c.user.nickname,
                module_id=c.module_id, module_name=c.module.name if c.module else None,
                task=c.task, task_as_string=c.task_as_string, priority=c.priority, comment=c.comment,
            )
            for c in event.choices
        ],
        flights=[
            FlightOut(
                id=f.id, name=f.name, mission=f.mission, aircraft_id=f.aircraft_id,
                aircraft_name=f.aircraft.name if f.aircraft else None, nb_slots=f.nb_slots,
                slots=[
                    SlotOut(id=s.id, user_id=s.user_id, user_nickname=s.user.nickname if s.user else None, username=s.username)
                    for s in f.slots
                ],
            )
            for f in event.flights
        ],
    )


@router.post("/events", response_model=EventDetailOut, status_code=status.HTTP_201_CREATED)
async def create_event(data: EventCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not can_add_event(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    now = datetime.now(timezone.utc)
    event = CalendarEvent(
        title=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        type=data.type,
        sim_dcs=data.sim_dcs,
        sim_bms=data.sim_bms,
        description=data.description,
        restrictions=",".join(str(r) for r in data.restrictions) if data.restrictions else None,
        registration=data.registration,
        ato=data.ato,
        repeat_event=data.repeat_event,
        map_id=data.map_id,
        server_id=data.server_id,
        owner_id=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return await get_event(event.id, db)


@router.put("/events/{event_id}", response_model=EventDetailOut)
async def update_event(event_id: int, data: EventUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = await db.get(CalendarEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not can_edit_event(user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    event.title = data.title
    event.start_date = data.start_date
    event.end_date = data.end_date
    event.type = data.type
    event.sim_dcs = data.sim_dcs
    event.sim_bms = data.sim_bms
    event.description = data.description
    event.restrictions = ",".join(str(r) for r in data.restrictions) if data.restrictions else None
    event.registration = data.registration
    event.ato = data.ato
    event.repeat_event = data.repeat_event
    event.map_id = data.map_id
    event.server_id = data.server_id
    event.debrief = data.debrief
    event.updated_at = datetime.now(timezone.utc)

    await db.commit()
    return await get_event(event_id, db)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = await db.get(CalendarEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not can_delete_event(user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    event.deleted = True
    event.deleted_at = datetime.now(timezone.utc)
    event.updated_at = datetime.now(timezone.utc)
    await db.commit()


@router.post("/events/{event_id}/copy", response_model=EventDetailOut, status_code=status.HTTP_201_CREATED)
async def copy_event(event_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not can_add_event(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id).options(selectinload(CalendarEvent.modules))
    )
    source = result.scalar_one_or_none()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    now = datetime.now(timezone.utc)
    new_event = CalendarEvent(
        title=source.title,
        start_date=source.start_date,
        end_date=source.end_date,
        type=source.type,
        sim_dcs=source.sim_dcs,
        sim_bms=source.sim_bms,
        description=source.description,
        restrictions=source.restrictions,
        registration=source.registration,
        ato=source.ato,
        repeat_event=CalendarEvent.REPEAT_NONE,
        map_id=source.map_id,
        server_id=source.server_id,
        owner_id=user.id,
        created_at=now,
        updated_at=now,
    )
    for m in source.modules:
        new_event.modules.append(m)

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return await get_event(new_event.id, db)


@router.post("/events/{event_id}/vote", response_model=VoteOut)
async def vote_event(event_id: int, data: VoteCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = await db.get(CalendarEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not can_vote_event(user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Upsert vote
    result = await db.execute(select(Vote).where(Vote.event_id == event_id, Vote.user_id == user.id))
    vote = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if vote:
        vote.vote = data.vote
        vote.comment = data.comment
        vote.updated_at = now
    else:
        vote = Vote(event_id=event_id, user_id=user.id, vote=data.vote, comment=data.comment, created_at=now, updated_at=now)
        db.add(vote)

    await db.commit()
    await db.refresh(vote)

    return VoteOut(id=vote.id, user_id=vote.user_id, user_nickname=user.nickname, vote=vote.vote, comment=vote.comment, created_at=vote.created_at)


@router.post("/events/{event_id}/choices", response_model=ChoiceOut)
async def add_choice(event_id: int, data: ChoiceCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = await db.get(CalendarEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not can_choose_event(user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    now = datetime.now(timezone.utc)
    choice = Choice(
        event_id=event_id, user_id=user.id, module_id=data.module_id,
        task=data.task, priority=data.priority, comment=data.comment,
        created_at=now, updated_at=now,
    )
    db.add(choice)
    await db.commit()
    await db.refresh(choice)

    result = await db.execute(select(Choice).where(Choice.id == choice.id).options(selectinload(Choice.module)))
    choice = result.scalar_one()

    return ChoiceOut(
        id=choice.id, user_id=choice.user_id, user_nickname=user.nickname,
        module_id=choice.module_id, module_name=choice.module.name if choice.module else None,
        task=choice.task, task_as_string=choice.task_as_string, priority=choice.priority, comment=choice.comment,
    )


@router.put("/choices/{choice_id}", response_model=ChoiceOut)
async def update_choice(choice_id: int, data: ChoiceUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Choice).where(Choice.id == choice_id).options(selectinload(Choice.module)))
    choice = result.scalar_one_or_none()
    if choice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if choice.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if data.module_id is not None:
        choice.module_id = data.module_id
    if data.task is not None:
        choice.task = data.task
    if data.priority is not None:
        choice.priority = data.priority
    if data.comment is not None:
        choice.comment = data.comment

    choice.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(choice)

    result = await db.execute(select(Choice).where(Choice.id == choice.id).options(selectinload(Choice.module)))
    choice = result.scalar_one()

    return ChoiceOut(
        id=choice.id, user_id=choice.user_id, user_nickname=user.nickname,
        module_id=choice.module_id, module_name=choice.module.name if choice.module else None,
        task=choice.task, task_as_string=choice.task_as_string, priority=choice.priority, comment=choice.comment,
    )


@router.post("/mark-all-viewed")
async def mark_all_viewed(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))
    )
    notifications = result.scalars().all()
    now = datetime.now(timezone.utc)
    for n in notifications:
        n.read_at = now
    await db.commit()
    return {"detail": f"Marked {len(notifications)} notifications as read"}
