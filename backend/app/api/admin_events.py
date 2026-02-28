from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.calendar import CalendarEvent, Choice, Flight, Slot, Vote
from app.models.user import User
from app.schemas.calendar import (
    AdminEventListOut,
    AdminEventOut,
    ChoiceOut,
    EventDetailOut,
    FlightOut,
    SlotOut,
    VoteOut,
)

router = APIRouter(prefix="/admin/events", tags=["admin-events"])


def _build_admin_event_out(event: CalendarEvent) -> AdminEventOut:
    """Build an AdminEventOut DTO from a CalendarEvent model instance."""
    return AdminEventOut(
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
        deleted=event.deleted,
        deleted_at=event.deleted_at,
        owner_id=event.owner_id,
        owner_nickname=event.owner.nickname if event.owner else None,
        map_name=event.map.name if event.map else None,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get("", response_model=AdminEventListOut)
async def list_events(
    search: str | None = Query(None),
    type_filter: int | None = Query(None, alias="type"),
    deleted: bool | None = Query(None),
    sim: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(CalendarEvent)

    if search:
        pattern = f"%{search}%"
        query = query.where(CalendarEvent.title.ilike(pattern))

    if type_filter is not None:
        query = query.where(CalendarEvent.type == type_filter)

    if deleted is not None:
        query = query.where(CalendarEvent.deleted == deleted)

    if sim == "dcs":
        query = query.where(CalendarEvent.sim_dcs == True)  # noqa: E712
    elif sim == "bms":
        query = query.where(CalendarEvent.sim_bms == True)  # noqa: E712

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.where(CalendarEvent.start_date >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.where(CalendarEvent.start_date <= dt_to)
        except ValueError:
            pass

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page
    query = (
        query.options(selectinload(CalendarEvent.owner), selectinload(CalendarEvent.map))
        .order_by(CalendarEvent.start_date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    events = result.scalars().all()

    return AdminEventListOut(
        items=[_build_admin_event_out(e) for e in events],
        total=total,
    )


@router.get("/{event_id}", response_model=EventDetailOut)
async def get_event(
    event_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
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
            selectinload(CalendarEvent.server),
        )
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement non trouvé")

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
        server_name=event.server.name if event.server else None,
        image_id=event.image_id,
        image_uuid=event.image.uuid if event.image else None,
        owner_id=event.owner_id,
        module_ids=[m.id for m in event.modules],
        module_names=[m.name for m in event.modules],
        restriction_labels=[CalendarEvent.RESTRICTIONS.get(r, "inconnu") for r in event.get_restrictions_list()],
        votes=[
            VoteOut(
                id=v.id,
                user_id=v.user_id,
                user_nickname=v.user.nickname,
                vote=v.vote,
                comment=v.comment,
                created_at=v.created_at,
            )
            for v in event.votes
        ],
        choices=[
            ChoiceOut(
                id=c.id,
                user_id=c.user_id,
                user_nickname=c.user.nickname,
                module_id=c.module_id,
                module_name=c.module.name if c.module else None,
                module_type=c.module.type if c.module else None,
                task=c.task,
                task_as_string=c.task_as_string,
                priority=c.priority,
                comment=c.comment,
            )
            for c in event.choices
        ],
        flights=[
            FlightOut(
                id=f.id,
                name=f.name,
                mission=f.mission,
                aircraft_id=f.aircraft_id,
                aircraft_name=f.aircraft.name if f.aircraft else None,
                nb_slots=f.nb_slots,
                slots=[
                    SlotOut(
                        id=s.id,
                        user_id=s.user_id,
                        user_nickname=s.user.nickname if s.user else None,
                        username=s.username,
                    )
                    for s in f.slots
                ],
            )
            for f in event.flights
        ],
    )


@router.patch("/{event_id}/restore", response_model=AdminEventOut)
async def restore_event(
    event_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.id == event_id)
        .options(selectinload(CalendarEvent.owner), selectinload(CalendarEvent.map))
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement non trouvé")
    if not event.deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'événement n'est pas supprimé")

    event.deleted = False
    event.deleted_at = None
    event.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(event)

    return _build_admin_event_out(event)
