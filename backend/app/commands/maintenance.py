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
    from datetime import UTC, datetime, timedelta
    from zoneinfo import ZoneInfo

    from sqlalchemy import select

    from app.database import AsyncSessionLocal, engine
    from app.models.calendar import CalendarEvent

    PARIS_TZ = ZoneInfo("Europe/Paris")

    def _reinterpret(dt: datetime | None) -> datetime | None:
        """Reinterpret a UTC datetime as Europe/Paris local time. Skip if None or already non-UTC."""
        if dt is None:
            return None
        if dt.tzinfo is not None and dt.tzinfo != UTC and dt.utcoffset() != timedelta(0):
            return dt  # already non-UTC, skip to avoid double-shifting
        return dt.replace(tzinfo=None).replace(tzinfo=PARIS_TZ)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CalendarEvent))
        events = result.scalars().all()

        fixed = 0
        skipped = 0
        for event in events:
            if not event.start_date or not event.end_date:
                skipped += 1
                continue

            new_start = _reinterpret(event.start_date)
            new_end = _reinterpret(event.end_date)

            # Skip if nothing changed (already fixed or non-UTC)
            if new_start == event.start_date and new_end == event.end_date:
                skipped += 1
                continue

            if dry_run:
                rprint(
                    f"  [bold cyan]\\[dry-run][/bold cyan] event {event.id}: "
                    f"{event.start_date.isoformat()} -> {new_start.astimezone(UTC).isoformat()}"
                )
            else:
                event.start_date = new_start
                event.end_date = new_end
                event.created_at = _reinterpret(event.created_at)
                event.updated_at = _reinterpret(event.updated_at)
                event.deleted_at = _reinterpret(event.deleted_at)
                fixed += 1

        if not dry_run:
            await session.commit()
            rprint(f"[bold green]Fixed {fixed} events, skipped {skipped}.[/bold green]")
        else:
            rprint(f"\n[bold]Dry run complete. {len(events) - skipped} events would be updated, {skipped} skipped.[/bold]")

    await engine.dispose()


@maintenance_app.command("fix-event-timezones")
def fix_event_timezones(
    dry_run: bool = typer.Option(True, help="Preview changes without updating the DB"),
) -> None:
    """Fix calendar event dates shifted by wrong timezone assumption during import."""
    if not dry_run:
        typer.confirm("This will update start_date/end_date for ALL calendar events. Continue?", abort=True)
    asyncio.run(_fix_event_timezones(dry_run))


async def _convert_images_to_webp(dry_run: bool) -> None:
    """Convert all non-WebP uploaded images to WebP format."""
    import io

    from PIL import Image, ImageOps
    from sqlalchemy import select

    from app.database import AsyncSessionLocal, engine
    from app.models.content import File

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(File).where(File.type == File.TYPE_IMAGE, File.mime_type != "image/webp")
        )
        files = result.scalars().all()

        if not files:
            rprint("[bold green]No images to convert.[/bold green]")
            await engine.dispose()
            return

        rprint(f"Found [bold]{len(files)}[/bold] image(s) to convert.\n")

        converted = 0
        missing = 0
        errors = 0
        old_files_to_remove: list[str] = []

        for f in files:
            old_path = os.path.join(settings.UPLOAD_DIR, f.uuid[0], f.uuid[1], f"{f.uuid}.{f.extension}")
            new_path = os.path.join(settings.UPLOAD_DIR, f.uuid[0], f.uuid[1], f"{f.uuid}.webp")

            if not os.path.exists(old_path):
                rprint(f"  [bold yellow]\\[missing][/bold yellow] {f.uuid}.{f.extension}")
                missing += 1
                continue

            if dry_run:
                old_size = os.path.getsize(old_path)
                rprint(f"  [bold cyan]\\[dry-run][/bold cyan] would convert {f.uuid}.{f.extension} ({old_size} bytes) -> .webp")
                converted += 1
                continue

            try:
                img = ImageOps.exif_transpose(Image.open(old_path))
                buf = io.BytesIO()
                img.save(buf, format="WEBP", quality=85, method=6)
                webp_data = buf.getvalue()

                with open(new_path, "wb") as out:
                    out.write(webp_data)

                old_size = f.size
                f.extension = "webp"
                f.mime_type = "image/webp"
                f.size = len(webp_data)

                if old_path != new_path:
                    old_files_to_remove.append(old_path)

                rprint(f"  [bold green]\\[converted][/bold green] {f.uuid} ({old_size} -> {f.size} bytes)")
                converted += 1
            except Exception as e:
                rprint(f"  [bold red]\\[error][/bold red] {f.uuid}: {e}")
                errors += 1

        if not dry_run:
            await session.commit()
            # Remove old files only after successful commit
            for old_path in old_files_to_remove:
                try:
                    os.remove(old_path)
                except OSError:
                    pass

    await engine.dispose()

    rprint(f"\n[bold]Done.[/bold] converted=[green]{converted}[/green], missing=[yellow]{missing}[/yellow], errors=[red]{errors}[/red]")
    if dry_run and converted > 0:
        rprint("[bold]Run with --no-dry-run to apply changes.[/bold]")


@maintenance_app.command("convert-images-to-webp")
def convert_images_to_webp(
    dry_run: bool = typer.Option(True, help="Preview changes without converting files"),
) -> None:
    """Convert all non-WebP uploaded images to WebP format."""
    if not dry_run:
        typer.confirm("Ceci va convertir toutes les images (jpg/png) en WebP. Continuer ?", abort=True)
    asyncio.run(_convert_images_to_webp(dry_run))


@maintenance_app.command("fix-filenames")
def fix_filenames(
    dry_run: bool = typer.Option(True, help="Preview changes without renaming files"),
) -> None:
    """Rename uploaded files to add their extension (fixes legacy import)."""
    asyncio.run(_fix_filenames(dry_run))
