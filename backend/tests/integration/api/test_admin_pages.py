"""Integration tests for admin pages (CMS) endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.models.content import Page, PageBlock
from tests.factories import AdminFactory, PageBlockFactory, PageFactory, UserFactory


async def _create_admin(db: AsyncSession) -> tuple:
    """Create an admin user and return (user, auth_headers)."""
    user = AdminFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_user(db: AsyncSession) -> tuple:
    """Create a regular user and return (user, auth_headers)."""
    user = UserFactory.build()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.get_roles_list())
    return user, {"Authorization": f"Bearer {token}"}


async def _create_page(db: AsyncSession, **overrides) -> Page:
    """Create and return a page."""
    page = PageFactory.build(**overrides)
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


async def _create_page_with_blocks(db: AsyncSession, n: int = 2, **page_overrides) -> Page:
    """Create a page with n blocks and return the page."""
    page = PageFactory.build(**page_overrides)
    db.add(page)
    await db.commit()
    await db.refresh(page)

    for i in range(1, n + 1):
        block = PageBlockFactory.build(page_id=page.id, number=i)
        db.add(block)
    await db.commit()
    await db.refresh(page)
    return page


# =============================================================================
# List pages — GET /api/admin/pages
# =============================================================================


@pytest.mark.asyncio
async def test_list_pages_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, title="Alpha", route="alpha", path="/alpha")
    await _create_page(db_session, title="Bravo", route="bravo", path="/bravo")

    # WHEN
    response = await client.get("/api/admin/pages", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_pages_search(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, title="Accueil", route="accueil", path="/accueil")
    await _create_page(db_session, title="Contact", route="contact", path="/contact")

    # WHEN
    response = await client.get("/api/admin/pages", params={"search": "accueil"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Accueil"


@pytest.mark.asyncio
async def test_list_pages_filter_enabled(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, title="Active", route="active", path="/active", enabled=True)
    await _create_page(db_session, title="Inactive", route="inactive", path="/inactive", enabled=False)

    # WHEN
    response = await client.get("/api/admin/pages", params={"enabled": "true"}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Active"


@pytest.mark.asyncio
async def test_list_pages_filter_restriction(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, title="Public", route="public", path="/public", restriction=Page.LEVEL_ALL)
    await _create_page(db_session, title="Members", route="members", path="/members", restriction=Page.LEVEL_MEMBER)

    # WHEN
    response = await client.get("/api/admin/pages", params={"restriction": Page.LEVEL_MEMBER}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Members"


@pytest.mark.asyncio
async def test_list_pages_pagination(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    for i in range(5):
        await _create_page(db_session, title=f"Page {i}", route=f"page{i}", path=f"/page{i}")

    # WHEN
    response = await client.get("/api/admin/pages", params={"skip": 2, "limit": 2}, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_pages_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.get("/api/admin/pages")

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_pages_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.get("/api/admin/pages", headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Create page — POST /api/admin/pages
# =============================================================================


@pytest.mark.asyncio
async def test_create_page_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Nouvelle page",
        "route": "nouvelle_page",
        "path": "/nouvelle-page",
        "enabled": True,
        "restriction": Page.LEVEL_MEMBER,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Nouvelle page"
    assert data["route"] == "nouvelle_page"
    assert data["path"] == "/nouvelle-page"
    assert data["enabled"] is True
    assert data["restriction"] == Page.LEVEL_MEMBER
    assert data["blocks"] == []
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_page_defaults(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Page par défaut",
        "route": "default",
        "path": "/default",
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["enabled"] is False
    assert data["restriction"] == 0


@pytest.mark.asyncio
async def test_create_page_duplicate_route(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, route="existing", path="/existing")

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Doublon",
        "route": "existing",
        "path": "/other",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_page_duplicate_path(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, route="original", path="/same-path")

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Doublon path",
        "route": "different_route",
        "path": "/same-path",
    }, headers=headers)

    # THEN
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_page_unauthenticated(client: AsyncClient):
    # GIVEN - no auth headers

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Nope",
        "route": "nope",
        "path": "/nope",
    })

    # THEN
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_page_unauthorized(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_user(db_session)

    # WHEN
    response = await client.post("/api/admin/pages", json={
        "title": "Nope",
        "route": "nope",
        "path": "/nope",
    }, headers=headers)

    # THEN
    assert response.status_code == 403


# =============================================================================
# Get page — GET /api/admin/pages/{page_id}
# =============================================================================


@pytest.mark.asyncio
async def test_get_page_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page_with_blocks(db_session, n=2, route="detail", path="/detail")

    # WHEN
    response = await client.get(f"/api/admin/pages/{page.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == page.id
    assert len(data["blocks"]) == 2
    # Blocks should be sorted by number
    assert data["blocks"][0]["number"] <= data["blocks"][1]["number"]


@pytest.mark.asyncio
async def test_get_page_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.get("/api/admin/pages/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Update page — PUT /api/admin/pages/{page_id}
# =============================================================================


@pytest.mark.asyncio
async def test_update_page_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page(db_session, title="Old Title", route="old", path="/old")

    # WHEN
    response = await client.put(f"/api/admin/pages/{page.id}", json={
        "title": "New Title",
        "route": "new",
        "path": "/new",
        "enabled": True,
        "restriction": Page.LEVEL_MEMBER,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["route"] == "new"
    assert data["path"] == "/new"
    assert data["enabled"] is True
    assert data["restriction"] == Page.LEVEL_MEMBER


@pytest.mark.asyncio
async def test_update_page_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/pages/9999", json={
        "title": "Nope",
        "route": "nope",
        "path": "/nope",
        "enabled": False,
        "restriction": 0,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_page_duplicate_route(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    await _create_page(db_session, route="taken", path="/taken")
    page = await _create_page(db_session, route="mine", path="/mine")

    # WHEN
    response = await client.put(f"/api/admin/pages/{page.id}", json={
        "title": page.title,
        "route": "taken",
        "path": "/mine",
        "enabled": page.enabled,
        "restriction": page.restriction,
    }, headers=headers)

    # THEN
    assert response.status_code == 409


# =============================================================================
# Delete page — DELETE /api/admin/pages/{page_id}
# =============================================================================


@pytest.mark.asyncio
async def test_delete_page_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/pages/{page.id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify deletion
    deleted = await db_session.get(Page, page.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_page_cascades_blocks(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page_with_blocks(db_session, n=2)
    page_id = page.id

    # Get block ids before deletion
    blocks = await db_session.execute(
        select(PageBlock).where(PageBlock.page_id == page_id)
    )
    block_ids = [b.id for b in blocks.scalars().all()]
    assert len(block_ids) == 2

    # WHEN
    response = await client.delete(f"/api/admin/pages/{page_id}", headers=headers)

    # THEN
    assert response.status_code == 204

    # Verify blocks are also deleted
    for block_id in block_ids:
        deleted_block = await db_session.get(PageBlock, block_id)
        assert deleted_block is None


@pytest.mark.asyncio
async def test_delete_page_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.delete("/api/admin/pages/9999", headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Create block — POST /api/admin/pages/{page_id}/blocks
# =============================================================================


@pytest.mark.asyncio
async def test_create_block_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page(db_session)

    # WHEN
    response = await client.post(f"/api/admin/pages/{page.id}/blocks", json={
        "content": "# Hello world",
        "number": 1,
        "enabled": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert len(data["blocks"]) == 1
    assert data["blocks"][0]["content"] == "# Hello world"
    assert data["blocks"][0]["enabled"] is True


@pytest.mark.asyncio
async def test_create_block_page_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.post("/api/admin/pages/9999/blocks", json={
        "content": "content",
        "number": 1,
        "enabled": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Update block — PUT /api/admin/pages/{page_id}/blocks/{block_id}
# =============================================================================


@pytest.mark.asyncio
async def test_update_block_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page_with_blocks(db_session, n=1)
    # Fetch block id
    blocks_result = await db_session.execute(
        select(PageBlock).where(PageBlock.page_id == page.id)
    )
    block = blocks_result.scalars().first()

    # WHEN
    response = await client.put(f"/api/admin/pages/{page.id}/blocks/{block.id}", json={
        "content": "Updated content",
        "number": 1,
        "enabled": False,
    }, headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    updated_block = next(b for b in data["blocks"] if b["id"] == block.id)
    assert updated_block["content"] == "Updated content"
    assert updated_block["enabled"] is False


@pytest.mark.asyncio
async def test_update_block_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page(db_session)

    # WHEN
    response = await client.put(f"/api/admin/pages/{page.id}/blocks/9999", json={
        "content": "nope",
        "number": 1,
        "enabled": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_block_page_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)

    # WHEN
    response = await client.put("/api/admin/pages/9999/blocks/1", json={
        "content": "nope",
        "number": 1,
        "enabled": True,
    }, headers=headers)

    # THEN
    assert response.status_code == 404


# =============================================================================
# Delete block — DELETE /api/admin/pages/{page_id}/blocks/{block_id}
# =============================================================================


@pytest.mark.asyncio
async def test_delete_block_success(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page_with_blocks(db_session, n=2)
    blocks_result = await db_session.execute(
        select(PageBlock).where(PageBlock.page_id == page.id)
    )
    blocks = blocks_result.scalars().all()
    block_to_delete = blocks[0]

    # WHEN
    response = await client.delete(f"/api/admin/pages/{page.id}/blocks/{block_to_delete.id}", headers=headers)

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) == 1
    assert all(b["id"] != block_to_delete.id for b in data["blocks"])


@pytest.mark.asyncio
async def test_delete_block_not_found(client: AsyncClient, db_session: AsyncSession):
    # GIVEN
    _, headers = await _create_admin(db_session)
    page = await _create_page(db_session)

    # WHEN
    response = await client.delete(f"/api/admin/pages/{page.id}/blocks/9999", headers=headers)

    # THEN
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_block_renormalizes(client: AsyncClient, db_session: AsyncSession):
    # GIVEN - page with 3 blocks numbered 1, 2, 3
    _, headers = await _create_admin(db_session)
    page = await _create_page_with_blocks(db_session, n=3)
    blocks_result = await db_session.execute(
        select(PageBlock).where(PageBlock.page_id == page.id).order_by(PageBlock.number)
    )
    blocks = blocks_result.scalars().all()
    middle_block = blocks[1]  # number=2

    # WHEN - delete the middle block
    response = await client.delete(f"/api/admin/pages/{page.id}/blocks/{middle_block.id}", headers=headers)

    # THEN - remaining blocks should be renormalized to 1, 2
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) == 2
    numbers = [b["number"] for b in data["blocks"]]
    assert numbers == [1, 2]
