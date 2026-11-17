import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import MenuItem
from tests.factories import MenuItemFactory


async def _create_menu_item(db: AsyncSession, **overrides) -> MenuItem:
    item = MenuItemFactory.build(**overrides)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@pytest.mark.asyncio
async def test_menu_hides_retired_teamspeak_item(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    await _create_menu_item(db_session, label="Discord", type=MenuItem.TYPE_DISCORD_VOICE, link=None)
    await _create_menu_item(db_session, label="Teamspeak", type=MenuItem.TYPE_TEAMSPEAK, link=None)

    # WHEN
    response = await client.get("/api/menu")

    # THEN
    assert response.status_code == 200
    labels = [item["label"] for item in response.json()]
    assert labels == ["Discord"]


@pytest.mark.asyncio
async def test_menu_hides_retired_child_item(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    parent = await _create_menu_item(db_session, label="Communauté", type=MenuItem.TYPE_MENU, link=None)
    await _create_menu_item(db_session, label="Discord", type=MenuItem.TYPE_DISCORD_VOICE, link=None, menu_id=parent.id)
    await _create_menu_item(db_session, label="Teamspeak", type=MenuItem.TYPE_TEAMSPEAK, link=None, menu_id=parent.id)

    # WHEN
    response = await client.get("/api/menu")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert [item["label"] for item in data] == ["Communauté"]
    assert [child["label"] for child in data[0]["items"]] == ["Discord"]


def test_teamspeak_type_not_offered_in_admin():
    # GIVEN / WHEN / THEN
    assert MenuItem.TYPE_TEAMSPEAK not in MenuItem.TYPES
