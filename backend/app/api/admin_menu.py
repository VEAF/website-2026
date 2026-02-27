from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.content import MenuItem, Page, Url
from app.models.user import User
from app.schemas.content import (
    AdminMenuItemListOut,
    AdminMenuItemOut,
    AdminMenuItemTreeOut,
    MenuItemCreate,
    MenuItemReorderRequest,
    MenuItemUpdate,
)

router = APIRouter(prefix="/admin/menu", tags=["admin-menu"])


def _build_admin_item_out(item: MenuItem) -> AdminMenuItemOut:
    return AdminMenuItemOut(
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
        menu_id=item.menu_id,
        menu_label=item.menu.label if item.menu else None,
        url_id=item.url_id,
        url_slug=item.url.slug if item.url else None,
        page_id=item.page_id,
        page_title=item.page.title if item.page else None,
    )


def _build_tree_out(item: MenuItem) -> AdminMenuItemTreeOut:
    children = [_build_tree_out(child) for child in item.items] if item.items else []
    return AdminMenuItemTreeOut(
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
        menu_id=item.menu_id,
        url_id=item.url_id,
        url_slug=item.url.slug if item.url else None,
        page_id=item.page_id,
        page_title=item.page.title if item.page else None,
        items=children,
    )


def _clean_fields_by_type(item: MenuItem) -> None:
    """Clear unused reference fields based on item type."""
    if item.type == MenuItem.TYPE_URL:
        item.page_id = None
        item.link = None
    elif item.type == MenuItem.TYPE_PAGE:
        item.url_id = None
        item.link = None
    elif item.type == MenuItem.TYPE_LINK:
        item.page_id = None
        item.url_id = None
    elif item.type not in (MenuItem.TYPE_URL, MenuItem.TYPE_PAGE, MenuItem.TYPE_LINK):
        item.url_id = None
        item.page_id = None
        item.link = None


async def _validate_menu_item(data: MenuItemCreate | MenuItemUpdate, db: AsyncSession, exclude_id: int | None = None) -> None:
    """Validate type-specific required fields and foreign key references."""
    if data.type == MenuItem.TYPE_LINK and not data.link:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le champ 'link' est requis pour le type 'Url personnalisée'")

    if data.type == MenuItem.TYPE_URL:
        if not data.url_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le champ 'url' est requis pour le type 'Url (redirection)'")
        url = await db.get(Url, data.url_id)
        if url is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'URL référencée n'existe pas")

    if data.type == MenuItem.TYPE_PAGE:
        if not data.page_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le champ 'page' est requis pour le type 'Page'")
        page = await db.get(Page, data.page_id)
        if page is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La page référencée n'existe pas")

    if data.menu_id is not None:
        if exclude_id is not None and data.menu_id == exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un élément ne peut pas être son propre parent")
        parent = await db.get(MenuItem, data.menu_id)
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le menu parent n'existe pas")
        if parent.type != MenuItem.TYPE_MENU:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le parent doit être de type 'Menu'")


async def _get_item_with_relations(item_id: int, db: AsyncSession) -> MenuItem:
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.id == item_id)
        .options(selectinload(MenuItem.menu), selectinload(MenuItem.url), selectinload(MenuItem.page))
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Élément de menu non trouvé")
    return item


@router.get("", response_model=AdminMenuItemListOut)
async def list_menu_items(
    search: str | None = Query(None),
    type_filter: int | None = Query(None, alias="type"),
    enabled: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        filters.append(MenuItem.label.ilike(f"%{search}%"))
    if type_filter is not None:
        filters.append(MenuItem.type == type_filter)
    if enabled is not None:
        filters.append(MenuItem.enabled == enabled)

    count_q = select(func.count()).select_from(MenuItem)
    for f in filters:
        count_q = count_q.where(f)
    total = (await db.execute(count_q)).scalar_one()

    query = select(MenuItem).options(selectinload(MenuItem.menu), selectinload(MenuItem.url), selectinload(MenuItem.page))
    for f in filters:
        query = query.where(f)

    query = query.order_by(MenuItem.menu_id.asc().nulls_first(), MenuItem.position.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return AdminMenuItemListOut(
        items=[_build_admin_item_out(item) for item in items],
        total=total,
    )


@router.get("/tree", response_model=list[AdminMenuItemTreeOut])
async def get_menu_tree(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
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
    return [_build_tree_out(item) for item in root_items]


@router.post("", response_model=AdminMenuItemOut, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    data: MenuItemCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await _validate_menu_item(data, db)

    item = MenuItem(
        label=data.label,
        type=data.type,
        icon=data.icon,
        theme_classes=data.theme_classes,
        enabled=data.enabled,
        position=data.position,
        link=data.link,
        restriction=data.restriction,
        menu_id=data.menu_id,
        url_id=data.url_id,
        page_id=data.page_id,
    )
    _clean_fields_by_type(item)

    db.add(item)
    await db.commit()

    item = await _get_item_with_relations(item.id, db)
    return _build_admin_item_out(item)


@router.get("/{item_id}", response_model=AdminMenuItemOut)
async def get_menu_item(
    item_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = await _get_item_with_relations(item_id, db)
    return _build_admin_item_out(item)


@router.put("/reorder", response_model=list[AdminMenuItemTreeOut])
async def reorder_menu_items(
    data: MenuItemReorderRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Load all menu items
    result = await db.execute(select(MenuItem))
    all_items = {item.id: item for item in result.scalars().all()}

    for entry in data.items:
        item = all_items.get(entry.id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Élément de menu {entry.id} non trouvé")

        if entry.menu_id is not None:
            parent = all_items.get(entry.menu_id)
            if parent is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent {entry.menu_id} non trouvé")
            if parent.type != MenuItem.TYPE_MENU:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Le parent {entry.menu_id} doit être de type 'Menu'")

        item.menu_id = entry.menu_id
        item.position = entry.position

    await db.commit()

    # Return refreshed tree
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
    return [_build_tree_out(item) for item in root_items]


@router.put("/{item_id}", response_model=AdminMenuItemOut)
async def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = await db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Élément de menu non trouvé")

    await _validate_menu_item(data, db, exclude_id=item_id)

    item.label = data.label
    item.type = data.type
    item.icon = data.icon
    item.theme_classes = data.theme_classes
    item.enabled = data.enabled
    item.position = data.position
    item.link = data.link
    item.restriction = data.restriction
    item.menu_id = data.menu_id
    item.url_id = data.url_id
    item.page_id = data.page_id
    _clean_fields_by_type(item)

    await db.commit()

    item = await _get_item_with_relations(item_id, db)
    return _build_admin_item_out(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = await db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Élément de menu non trouvé")

    # Check for children
    children_count = (await db.execute(select(func.count()).where(MenuItem.menu_id == item_id))).scalar_one()
    if children_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de supprimer un menu qui contient des éléments",
        )

    await db.delete(item)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
