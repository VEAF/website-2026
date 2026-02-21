from app.database import AsyncSessionLocal, engine


async def load_all() -> None:
    """Load all fixture data in dependency order."""
    import app.models  # noqa: F401

    from fixtures.calendar import load_calendar_events
    from fixtures.content import load_content
    from fixtures.modules import load_modules
    from fixtures.reference import load_reference_data
    from fixtures.user_modules import load_user_modules
    from fixtures.users import load_users

    async with AsyncSessionLocal() as session:
        # Level 1: Reference data (no FK dependencies)
        roles, systems, servers = await load_reference_data(session)

        # Level 2: Modules (depends on roles, systems)
        modules = await load_modules(session, roles, systems)

        # Level 3: Independent entities
        users = await load_users(session)
        await load_content(session)

        # Level 4: Cross-references
        await load_user_modules(session, users, modules)
        await load_calendar_events(session, users, modules, servers)

        await session.commit()

    await engine.dispose()
