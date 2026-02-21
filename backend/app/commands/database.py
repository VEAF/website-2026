import asyncio

import typer

database_app = typer.Typer(help="Database management commands")


async def _drop_tables() -> None:
    import app.models  # noqa: F401
    from app.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _create_tables() -> None:
    import app.models  # noqa: F401
    from app.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _load_fixtures() -> None:
    from fixtures import load_all

    await load_all()


@database_app.command()
def drop() -> None:
    """Drop all database tables."""
    typer.confirm("This will DROP all tables. Continue?", abort=True)
    asyncio.run(_drop_tables())
    typer.echo("All tables dropped.")


@database_app.command()
def create() -> None:
    """Create all database tables from models."""
    asyncio.run(_create_tables())
    typer.echo("All tables created.")


@database_app.command()
def fixtures() -> None:
    """Drop tables, recreate schema, and load seed data."""
    asyncio.run(_drop_tables())
    typer.echo("Tables dropped.")
    asyncio.run(_create_tables())
    typer.echo("Tables created.")
    asyncio.run(_load_fixtures())
    typer.echo("Fixtures loaded.")
