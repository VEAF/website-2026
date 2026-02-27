import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.content import MenuItem
from tests.factories import AdminFactory, MenuItemFactory, PageFactory, UrlFactory, UserFactory


async def _create_admin(db: AsyncSession):
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession):
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_menu_item(db: AsyncSession, **overrides) -> MenuItem:
    item = MenuItemFactory.build(**overrides)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# ── List ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_menu_items_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_menu_item(db_session, label="News", position=1)
    await _create_menu_item(db_session, label="Forum", position=2)

    # WHEN
    response = await client.get("/api/admin/menu", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_menu_items_search(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_menu_item(db_session, label="Actualités")
    await _create_menu_item(db_session, label="Forum")

    # WHEN
    response = await client.get("/api/admin/menu", headers=headers, params={"search": "actu"})

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["label"] == "Actualités"


@pytest.mark.asyncio
async def test_list_menu_items_filter_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_menu_item(db_session, type=MenuItem.TYPE_MENU, link=None)
    await _create_menu_item(db_session, type=MenuItem.TYPE_LINK)

    # WHEN
    response = await client.get("/api/admin/menu", headers=headers, params={"type": MenuItem.TYPE_MENU})

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == MenuItem.TYPE_MENU


@pytest.mark.asyncio
async def test_list_menu_items_filter_enabled(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_menu_item(db_session, enabled=True)
    await _create_menu_item(db_session, enabled=False)

    # WHEN
    response = await client.get("/api/admin/menu", headers=headers, params={"enabled": True})

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["enabled"] is True


@pytest.mark.asyncio
async def test_list_menu_items_unauthenticated(client: AsyncClient):
    # WHEN
    response = await client.get("/api/admin/menu")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_menu_items_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/menu", headers=headers)

    # THEN
    assert response.status_code == 403


# ── Tree ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tree_returns_hierarchical_structure(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    parent = await _create_menu_item(db_session, label="Parent", type=MenuItem.TYPE_MENU, position=1, link=None)
    await _create_menu_item(db_session, label="Child", type=MenuItem.TYPE_LINK, position=1, menu_id=parent.id)

    # WHEN
    response = await client.get("/api/admin/menu/tree", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["label"] == "Parent"
    assert len(data[0]["items"]) == 1
    assert data[0]["items"][0]["label"] == "Child"


@pytest.mark.asyncio
async def test_tree_orders_by_position(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_menu_item(db_session, label="Second", position=2)
    await _create_menu_item(db_session, label="First", position=1)

    # WHEN
    response = await client.get("/api/admin/menu/tree", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data[0]["label"] == "First"
    assert data[1]["label"] == "Second"


# ── Create ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_link_item(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "External", "type": MenuItem.TYPE_LINK, "link": "https://example.com", "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["label"] == "External"
    assert data["type"] == MenuItem.TYPE_LINK
    assert data["link"] == "https://example.com"


@pytest.mark.asyncio
async def test_create_url_type_requires_url_id(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Redirect", "type": MenuItem.TYPE_URL, "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_page_type_requires_page_id(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Page Link", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_link_type_requires_link(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Link", "type": MenuItem.TYPE_LINK, "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_validates_parent_is_menu_type(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    non_menu_parent = await _create_menu_item(db_session, type=MenuItem.TYPE_LINK)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Child", "type": MenuItem.TYPE_LINK, "link": "https://test.com", "enabled": True, "position": 1, "restriction": 0, "menu_id": non_menu_parent.id},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_with_url_reference(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    url = UrlFactory.build()
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Redirect", "type": MenuItem.TYPE_URL, "url_id": url.id, "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["url_id"] == url.id
    assert data["url_slug"] == url.slug


@pytest.mark.asyncio
async def test_create_with_page_reference(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = PageFactory.build()
    db_session.add(page)
    await db_session.commit()
    await db_session.refresh(page)

    # WHEN
    response = await client.post(
        "/api/admin/menu",
        json={"label": "Custom Page", "type": MenuItem.TYPE_PAGE, "page_id": page.id, "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["page_id"] == page.id
    assert data["page_title"] == page.title


@pytest.mark.asyncio
async def test_create_unauthenticated(client: AsyncClient):
    # WHEN
    response = await client.post("/api/admin/menu", json={"label": "Test", "type": 2, "link": "https://test.com"})

    # THEN
    assert response.status_code == 401


# ── Get ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_item_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    item = await _create_menu_item(db_session, label="Test Item")

    # WHEN
    response = await client.get(f"/api/admin/menu/{item.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Test Item"
    assert data["id"] == item.id


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/menu/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# ── Update ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_item_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    item = await _create_menu_item(db_session, label="Old Label")

    # WHEN
    response = await client.put(
        f"/api/admin/menu/{item.id}",
        json={"label": "New Label", "type": MenuItem.TYPE_LINK, "link": "https://updated.com", "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "New Label"
    assert data["link"] == "https://updated.com"


@pytest.mark.asyncio
async def test_update_prevents_circular_parent(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    item = await _create_menu_item(db_session, type=MenuItem.TYPE_MENU, link=None)

    # WHEN
    response = await client.put(
        f"/api/admin/menu/{item.id}",
        json={"label": "Self Parent", "type": MenuItem.TYPE_MENU, "enabled": True, "position": 1, "restriction": 0, "menu_id": item.id},
        headers=headers,
    )

    # THEN
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_cleans_unused_fields(client: AsyncClient, db_session: AsyncSession):
    # GIVEN — Create a LINK item with a link value
    _, headers = await _create_admin(db_session)
    item = await _create_menu_item(db_session, type=MenuItem.TYPE_LINK, link="https://old.com")

    # WHEN — Change to TYPE_SERVERS (special type, should clear link)
    response = await client.put(
        f"/api/admin/menu/{item.id}",
        json={"label": "Servers", "type": MenuItem.TYPE_SERVERS, "enabled": True, "position": 1, "restriction": 0, "link": "https://old.com"},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["link"] is None
    assert data["url_id"] is None
    assert data["page_id"] is None


@pytest.mark.asyncio
async def test_update_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put(
        "/api/admin/menu/9999",
        json={"label": "Ghost", "type": MenuItem.TYPE_LINK, "link": "https://test.com", "enabled": True, "position": 1, "restriction": 0},
        headers=headers,
    )

    # THEN
    assert response.status_code == 404


# ── Delete ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_item_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    item = await _create_menu_item(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/menu/{item.id}", headers=headers)

    # THEN
    assert response.status_code == 204
    deleted = await db_session.get(MenuItem, item.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_prevents_if_has_children(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    parent = await _create_menu_item(db_session, type=MenuItem.TYPE_MENU, link=None)
    await _create_menu_item(db_session, menu_id=parent.id)

    # WHEN
    response = await client.delete(f"/api/admin/menu/{parent.id}", headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/menu/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# ── Reorder ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reorder_updates_positions(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    item1 = await _create_menu_item(db_session, label="First", position=1)
    item2 = await _create_menu_item(db_session, label="Second", position=2)

    # WHEN — Swap positions
    response = await client.put(
        "/api/admin/menu/reorder",
        json={"items": [{"id": item2.id, "menu_id": None, "position": 1}, {"id": item1.id, "menu_id": None, "position": 2}]},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data[0]["label"] == "Second"
    assert data[1]["label"] == "First"


@pytest.mark.asyncio
async def test_reorder_moves_to_different_parent(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    parent = await _create_menu_item(db_session, label="Parent", type=MenuItem.TYPE_MENU, position=1, link=None)
    child = await _create_menu_item(db_session, label="Child", position=2)

    # WHEN — Move child under parent
    response = await client.put(
        "/api/admin/menu/reorder",
        json={"items": [{"id": parent.id, "menu_id": None, "position": 1}, {"id": child.id, "menu_id": parent.id, "position": 1}]},
        headers=headers,
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Only parent at root
    assert data[0]["label"] == "Parent"
    assert len(data[0]["items"]) == 1
    assert data[0]["items"][0]["label"] == "Child"
