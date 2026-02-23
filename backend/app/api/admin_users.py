from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import AdminUserListOut, AdminUserOut, AdminUserUpdate

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


def _build_admin_user_out(user: User) -> AdminUserOut:
    """Build an AdminUserOut DTO from a User model instance."""
    return AdminUserOut(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        roles=user.get_roles_list(),
        status=user.status,
        status_as_string=user.status_as_string,
        sim_dcs=user.sim_dcs,
        sim_bms=user.sim_bms,
        discord=user.discord,
        forum=user.forum,
        need_presentation=user.need_presentation,
        cadet_flights=user.cadet_flights,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=AdminUserListOut)
async def list_users(
    search: str | None = Query(None),
    status_filter: int | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)

    if search:
        pattern = f"%{search}%"
        query = query.where(or_(User.nickname.ilike(pattern), User.email.ilike(pattern)))

    if status_filter is not None:
        query = query.where(User.status == status_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page
    query = query.order_by(User.nickname.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return AdminUserListOut(
        items=[_build_admin_user_out(u) for u in users],
        total=total,
    )


@router.get("/{user_id}", response_model=AdminUserOut)
async def get_user(
    user_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    return _build_admin_user_out(target)


@router.put("/{user_id}", response_model=AdminUserOut)
async def update_user(
    user_id: int,
    data: AdminUserUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    if data.status not in User.STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Statut invalide")

    target.email = data.email
    target.nickname = data.nickname
    target.roles = ",".join(data.roles) if data.roles else ""
    target.status = data.status
    target.discord = data.discord
    target.forum = data.forum
    target.sim_dcs = data.sim_dcs
    target.sim_bms = data.sim_bms
    target.need_presentation = data.need_presentation
    target.updated_at = datetime.now(UTC)

    try:
        await db.commit()
        await db.refresh(target)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email ou ce pseudo existe déjà",
        )

    return _build_admin_user_out(target)
