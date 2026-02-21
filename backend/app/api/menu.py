from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_optional_user
from app.auth.permissions import is_granted_to_level
from app.database import get_db
from app.models.content import MenuItem
from app.models.user import User
from app.schemas.content import MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])


def build_menu_tree(items: list[MenuItem], user: User | None) -> list[MenuItemOut]:
    result = []
    for item in items:
        if not item.enabled:
            continue
        if not is_granted_to_level(user, item.restriction):
            continue

        children = build_menu_tree(item.items, user) if item.items else []
        result.append(
            MenuItemOut(
                id=item.id,
                label=item.label,
                type=item.type,
                type_as_string=item.type_as_string,
                icon=item.icon,
                theme_classes=item.theme_classes,
                enabled=item.enabled,
                position=item.position,
                link=item.link,
                restriction=item.restriction,
                url_slug=item.url.slug if item.url else None,
                page_path=item.page.path if item.page else None,
                items=children,
            )
        )
    return result


@router.get("", response_model=list[MenuItemOut])
async def get_menu(user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.menu_id.is_(None))
        .options(
            selectinload(MenuItem.items).selectinload(MenuItem.items),
            selectinload(MenuItem.url),
            selectinload(MenuItem.page),
            selectinload(MenuItem.items).selectinload(MenuItem.url),
            selectinload(MenuItem.items).selectinload(MenuItem.page),
        )
        .order_by(MenuItem.position)
    )
    root_items = result.scalars().all()
    return build_menu_tree(list(root_items), user)
