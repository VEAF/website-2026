import asyncio

import typer
from rich import print as rprint

calendar_app = typer.Typer(help="Calendar commands", no_args_is_help=True)


async def _process_recurring_events() -> None:
    from app.database import AsyncSessionLocal, engine
    from app.services.calendar import check_recurring_events

    async with AsyncSessionLocal() as db:
        count = await check_recurring_events(db)

    await engine.dispose()

    if count > 0:
        rprint(f"[bold green]{count}[/bold green] event(s) created")
    else:
        rprint("[dim]No events to create[/dim]")


@calendar_app.command("auto")
def auto() -> None:
    """Créer les prochaines occurrences des événements périodiques."""
    asyncio.run(_process_recurring_events())
