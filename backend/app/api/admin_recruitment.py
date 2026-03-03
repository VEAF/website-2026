from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.recruitment import RecruitmentEvent
from app.models.user import User
from app.schemas.recruitment import AdminRecruitmentEventListOut, AdminRecruitmentEventOut, AdminRecruitmentEventUpdate

router = APIRouter(prefix="/admin/recruitment", tags=["admin-recruitment"])


def _build_admin_event_out(event: RecruitmentEvent) -> AdminRecruitmentEventOut:
    """Build an AdminRecruitmentEventOut DTO from a RecruitmentEvent model instance."""
    return AdminRecruitmentEventOut(
        id=event.id,
        type=event.type,
        type_as_string=event.type_as_string,
        event_at=event.event_at,
        comment=event.comment,
        ack_at=event.ack_at,
        user_id=event.user_id,
        user_nickname=event.user.nickname if event.user else None,
        validator_id=event.validator_id,
        validator_nickname=event.validator.nickname if event.validator else None,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get("", response_model=AdminRecruitmentEventListOut)
async def list_recruitment_events(
    search: str | None = Query(None),
    type_filter: int | None = Query(None, alias="type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(RecruitmentEvent)

    if search:
        pattern = f"%{search}%"
        query = query.where(RecruitmentEvent.user_id.in_(select(User.id).where(User.nickname.ilike(pattern))))

    if type_filter is not None:
        query = query.where(RecruitmentEvent.type == type_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page
    query = (
        query.options(selectinload(RecruitmentEvent.user), selectinload(RecruitmentEvent.validator))
        .order_by(RecruitmentEvent.event_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    events = result.scalars().all()

    return AdminRecruitmentEventListOut(
        items=[_build_admin_event_out(e) for e in events],
        total=total,
    )


@router.put("/{event_id}", response_model=AdminRecruitmentEventOut)
async def update_recruitment_event(
    event_id: int,
    data: AdminRecruitmentEventUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecruitmentEvent)
        .where(RecruitmentEvent.id == event_id)
        .options(selectinload(RecruitmentEvent.user), selectinload(RecruitmentEvent.validator))
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activité non trouvée")

    event.comment = data.comment
    event.event_at = data.event_at
    event.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(event, attribute_names=["user", "validator"])
    return _build_admin_event_out(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recruitment_event(
    event_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecruitmentEvent).where(RecruitmentEvent.id == event_id).options(selectinload(RecruitmentEvent.user))
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activité non trouvée")

    # Reverse side effects
    target = event.user
    if event.type == RecruitmentEvent.TYPE_ACTIVITY and target:
        target.cadet_flights = max(0, target.cadet_flights - 1)
        target.updated_at = datetime.now(UTC)
    elif event.type == RecruitmentEvent.TYPE_PRESENTATION and target:
        target.need_presentation = True
        target.updated_at = datetime.now(UTC)

    await db.delete(event)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
