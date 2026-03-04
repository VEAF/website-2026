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


async def _fix_event_timezones(dry_run: bool) -> None:
    """Reinterpret calendar event timestamps from UTC to Europe/Paris.

    The legacy YAML import incorrectly assumed Paris local times were UTC.
    For example, 21:00 CET was stored as 21:00 UTC instead of 20:00 UTC.
    This command reinterprets existing UTC timestamps as Paris local time.
    """
    from datetime import UTC
    from zoneinfo import ZoneInfo

    from sqlalchemy import select

    from app.database import AsyncSessionLocal, engine
    from app.models.calendar import CalendarEvent

    PARIS_TZ = ZoneInfo("Europe/Paris")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CalendarEvent))
        events = result.scalars().all()

        fixed = 0
        for event in events:
            # Reinterpret: the stored UTC value is actually a Paris local time
            new_start = event.start_date.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)
            new_end = event.end_date.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)

            if dry_run:
                rprint(
                    f"  [bold cyan]\\[dry-run][/bold cyan] event {event.id}: "
                    f"{event.start_date.isoformat()} -> {new_start.astimezone(UTC).isoformat()}"
                )
            else:
                event.start_date = new_start
                event.end_date = new_end
                # Also fix metadata timestamps if present
                if event.created_at:
                    event.created_at = event.created_at.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)
                if event.updated_at:
                    event.updated_at = event.updated_at.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)
                if event.deleted_at:
                    event.deleted_at = event.deleted_at.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)
                fixed += 1

        if not dry_run:
            await session.commit()
            rprint(f"[bold green]Fixed {fixed} events.[/bold green]")
        else:
            rprint(f"\n[bold]Dry run complete. {len(events)} events would be updated.[/bold]")

    await engine.dispose()


@maintenance_app.command("fix-event-timezones")
def fix_event_timezones(
    dry_run: bool = typer.Option(True, help="Preview changes without updating the DB"),
) -> None:
    """Fix calendar event dates shifted by wrong timezone assumption during import."""
    if not dry_run:
        typer.confirm("This will update start_date/end_date for ALL calendar events. Continue?", abort=True)
    asyncio.run(_fix_event_timezones(dry_run))


@maintenance_app.command("fix-filenames")
def fix_filenames(
    dry_run: bool = typer.Option(True, help="Preview changes without renaming files"),
) -> None:
    """Rename uploaded files to add their extension (fixes legacy import)."""
    asyncio.run(_fix_filenames(dry_run))
