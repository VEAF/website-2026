import asyncio
import os

import typer
from rich import print as rprint

from app.config import settings

maintenance_app = typer.Typer(help="Maintenance commands", no_args_is_help=True)


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


async def _fix_filenames(dry_run: bool) -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal, engine
    from app.models.content import File

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(File.uuid, File.extension))
        files = result.all()

    await engine.dispose()

    renamed = 0
    already_ok = 0
    missing = 0

    for uuid, extension in files:
        dir_path = os.path.join(settings.UPLOAD_DIR, uuid[0], uuid[1])
        path_with_ext = os.path.join(dir_path, f"{uuid}.{extension}")
        path_without_ext = os.path.join(dir_path, uuid)

        if os.path.exists(path_with_ext):
            already_ok += 1
            continue

        if os.path.exists(path_without_ext):
            if dry_run:
                rprint(f"  [bold cyan]\\[dry-run][/bold cyan] would rename {uuid} -> {uuid}.{extension}")
            else:
                os.rename(path_without_ext, path_with_ext)
                rprint(f"  [bold green]\\[renamed][/bold green] {uuid} -> {uuid}.{extension}")
            renamed += 1
        else:
            rprint(f"  [bold yellow]\\[missing][/bold yellow] file not found on disk for {uuid}")
            missing += 1

    rprint(f"\n[bold]Done.[/bold] already_ok=[green]{already_ok}[/green], renamed=[cyan]{renamed}[/cyan], missing=[yellow]{missing}[/yellow]")
    if dry_run and renamed > 0:
        rprint("[bold]Run with --no-dry-run to apply changes.[/bold]")


@maintenance_app.command("fix-filenames")
def fix_filenames(
    dry_run: bool = typer.Option(True, help="Preview changes without renaming files"),
) -> None:
    """Rename uploaded files to add their extension (fixes legacy import)."""
    asyncio.run(_fix_filenames(dry_run))
