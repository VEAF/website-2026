import asyncio

import typer

maintenance_app = typer.Typer(help="Maintenance commands")


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


@maintenance_app.command("import-yaml")
def import_yaml(
    filepath: str = typer.Option("var/website.yml", help="Path to the YAML fixture file"),
) -> None:
    """Drop tables, recreate schema, and import data from Symfony YAML export."""
    typer.confirm("This will DROP all tables and import from YAML. Continue?", abort=True)
    asyncio.run(_drop_tables())
    typer.echo("Tables dropped.")
    asyncio.run(_create_tables())
    typer.echo("Tables created.")
    asyncio.run(_import_from_yaml(filepath))
    typer.echo("Import complete.")


async def _import_from_yaml(filepath: str) -> None:
    from app.commands.import_yaml import run_import

    await run_import(filepath)
