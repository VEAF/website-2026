import asyncio

import typer
from rich import print as rprint

teamspeak_app = typer.Typer(help="TeamSpeak commands", no_args_is_help=True)


async def _check() -> None:
    from app.services.teamspeak import _fetch_ts_data_sync

    try:
        data = await asyncio.to_thread(_fetch_ts_data_sync)
        rprint(f"[bold green]OK[/bold green] — {data['client_count']} client(s), {len(data['channels'])} channel(s)")
        for ch in data["channels"]:
            if ch["clients"]:
                rprint(f"  [cyan]{ch['name']}[/cyan]")
                for cl in ch["clients"]:
                    rprint(f"    - {cl['nickname']}")
    except Exception as e:
        rprint(f"[bold red]Error[/bold red] — {e}")
    rprint("\n[dim]Note: this is a diagnostic command. It does not update the website cache.[/dim]")


@teamspeak_app.command("check")
def check() -> None:
    """Check TeamSpeak server connectivity and display current status."""
    rprint("[bold]Connecting to TeamSpeak server...[/bold]")
    asyncio.run(_check())
