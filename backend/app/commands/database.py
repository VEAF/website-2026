import asyncio

import typer
from rich import print as rprint

database_app = typer.Typer(help="Database management commands", no_args_is_help=True)


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


async def _exec_sql(statement) -> None:
    from app.database import engine

    async with engine.begin() as conn:
        await conn.execute(statement)
    await engine.dispose()


async def _has_data() -> bool:
    """Check if the user table has any data."""
    from sqlalchemy import text

    from app.database import engine

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT COUNT(*) FROM "user"'))
            count = result.scalar()
            return count > 0
    except Exception:
        return False
    finally:
        await engine.dispose()


def _run_migrations() -> None:
    """Drop alembic_version and run alembic upgrade head."""
    import subprocess

    from sqlalchemy import text

    asyncio.run(_exec_sql(text("DROP TABLE IF EXISTS alembic_version")))
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode != 0:
        rprint(f"[bold red]Migration failed: {result.stderr}[/bold red]")
        raise typer.Exit(1)
    rprint("[bold green]Tables created (via migrations).[/bold green]")


async def _load_fixtures() -> None:
    from fixtures import load_all

    await load_all()


@database_app.command()
def drop() -> None:
    """Drop all database tables."""
    typer.confirm("This will DROP all tables. Continue?", abort=True)
    asyncio.run(_drop_tables())
    rprint("[bold green]All tables dropped.[/bold green]")


@database_app.command()
def create() -> None:
    """Create all database tables from models."""
    asyncio.run(_create_tables())
    rprint("[bold green]All tables created.[/bold green]")


@database_app.command()
def fixtures(
    migrations: bool = typer.Option(True, "--migrations/--no-migrations", help="Use Alembic migrations (default) or create_all"),
    data: bool = typer.Option(True, "--data/--no-data", help="Load seed data after creating schema"),
) -> None:
    """Drop tables, recreate schema, and optionally load seed data."""
    if asyncio.run(_has_data()):
        typer.confirm("Users already exist in the database. This will DROP all data. Continue?", abort=True)
    asyncio.run(_drop_tables())
    rprint("[bold green]Tables dropped.[/bold green]")
    if migrations:
        _run_migrations()
    else:
        asyncio.run(_create_tables())
        rprint("[bold yellow]Tables created (without migration tracking).[/bold yellow]")
    if data:
        asyncio.run(_load_fixtures())
        rprint("[bold green]Fixtures loaded.[/bold green]")
    else:
        rprint("Seed data skipped.")
