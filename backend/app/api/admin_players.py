from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.dcs import Player
from app.models.user import User
from app.schemas.dcs import AdminPlayerListOut, PlayerCreate, PlayerOut, PlayerUpdate

router = APIRouter(prefix="/admin/players", tags=["admin-players"])


def _build_player_out(player: Player, linked_user: User | None) -> PlayerOut:
    """Build a PlayerOut DTO from a Player and its (optional) linked user."""
    return PlayerOut(
        id=player.id,
        ucid=player.ucid,
        nickname=player.nickname,
        join_at=player.join_at,
        last_join_at=player.last_join_at,
        user_id=linked_user.id if linked_user else None,
        user_nickname=linked_user.nickname if linked_user else None,
    )


async def _linked_user(db: AsyncSession, player: Player) -> User | None:
    """Return the user currently linked to this player, if any."""
    result = await db.execute(select(User).where(User.player_id == player.id))
    return result.scalars().first()


async def _apply_user_link(db: AsyncSession, player: Player, user_id: int | None) -> User | None:
    """Link the player to a user (or unlink it), and return the resulting linked user.

    The relation is owned by User.player_id, so any other user pointing to this player
    must be detached first.
    """
    result = await db.execute(select(User).where(User.player_id == player.id))
    for previous in result.scalars().all():
        if previous.id != user_id:
            previous.player_id = None

    if user_id is None:
        return None

    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    target.player_id = player.id
    return target


@router.get("", response_model=AdminPlayerListOut)
async def list_players(
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Player, User).outerjoin(User, User.player_id == Player.id)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Player.nickname.ilike(pattern),
                Player.ucid.ilike(pattern),
                User.nickname.ilike(pattern),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Player.nickname.asc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return AdminPlayerListOut(
        items=[_build_player_out(player, linked_user) for player, linked_user in result.all()],
        total=total,
    )


@router.post("", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
async def create_player(
    data: PlayerCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    player = Player(
        ucid=data.ucid,
        nickname=data.nickname,
    )
    db.add(player)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un joueur avec cet UCID existe déjà",
        )

    linked_user = await _apply_user_link(db, player, data.user_id)

    await db.commit()
    await db.refresh(player)

    return _build_player_out(player, linked_user)


@router.get("/{player_id}", response_model=PlayerOut)
async def get_player(
    player_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    player = await db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joueur non trouvé")
    return _build_player_out(player, await _linked_user(db, player))


@router.put("/{player_id}", response_model=PlayerOut)
async def update_player(
    player_id: int,
    data: PlayerUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    player = await db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joueur non trouvé")

    player.ucid = data.ucid
    player.nickname = data.nickname

    # Flush before touching the user link: _apply_user_link queries User, and the
    # resulting autoflush would raise the UCID conflict outside of this handler.
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un joueur avec cet UCID existe déjà",
        )

    linked_user = await _apply_user_link(db, player, data.user_id)

    await db.commit()
    await db.refresh(player)

    return _build_player_out(player, linked_user)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    player = await db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joueur non trouvé")

    # User owns the FK: detach it before deleting the player
    await _apply_user_link(db, player, None)

    await db.delete(player)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
