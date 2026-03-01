import asyncio

import typer

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
def fixtures(
    migrations: bool = typer.Option(False, "--migrations", help="Use Alembic migrations instead of create_all"),
    data: bool = typer.Option(True, "--data/--no-data", help="Load seed data after creating schema"),
) -> None:
    """Drop tables, recreate schema, and optionally load seed data."""
    asyncio.run(_drop_tables())
    typer.echo("Tables dropped.")
    if migrations:
        import subprocess

        from sqlalchemy import text

        asyncio.run(_exec_sql(text("DROP TABLE IF EXISTS alembic_version")))
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo(f"Migration failed: {result.stderr}", err=True)
            raise typer.Exit(1)
        typer.echo("Tables created (via migrations).")
    else:
        asyncio.run(_create_tables())
        typer.echo("Tables created.")
    if data:
        asyncio.run(_load_fixtures())
        typer.echo("Fixtures loaded.")
    else:
        typer.echo("Seed data skipped.")
