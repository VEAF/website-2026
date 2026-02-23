import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.database import Base, get_db
from app.main import app

# In-memory SQLite — schema created once per session for speed
_engine = create_async_engine("sqlite+aiosqlite://", echo=False)


@pytest.fixture(scope="session")
async def engine():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest.fixture(autouse=True)
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test session using savepoint (begin_nested) for isolation.

    App-level commit/rollback only affects the savepoint; the outer
    transaction is rolled back after each test to restore a clean DB.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        nested = await conn.begin_nested()

        session = AsyncSession(bind=conn, expire_on_commit=False)

        # When app code calls session.commit() or session.rollback(),
        # the savepoint ends. Restart it so subsequent operations still work.
        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(sync_session, sync_trans):
            if conn.sync_connection is not None and not conn.sync_connection.in_nested_transaction():
                sync_session.begin_nested()

        yield session
        await session.close()
        await trans.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def tmp_upload_dir(tmp_path):
    original = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path / "uploads")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield settings.UPLOAD_DIR
    settings.UPLOAD_DIR = original
