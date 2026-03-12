import asyncio

import typer
from rich import print as rprint

discord_app = typer.Typer(help="Discord commands", no_args_is_help=True)


async def _check() -> None:
    import httpx

    from app.config import settings

    token = settings.DISCORD_BOT_TOKEN
    guild_id = settings.DISCORD_GUILD_ID

    if not token or not guild_id:
        rprint("[bold red]Error[/bold red] — DISCORD_BOT_TOKEN and DISCORD_GUILD_ID must be set in .env")
        return

    base = "https://discord.com/api/v10"
    headers = {"Authorization": f"Bot {token}"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test bot token validity
        bot_resp = await client.get(f"{base}/users/@me", headers=headers)
        if bot_resp.status_code == 401:
            rprint("[bold red]Error[/bold red] — Invalid DISCORD_BOT_TOKEN (401 Unauthorized)")
            return
        bot_resp.raise_for_status()
        bot_data = bot_resp.json()
        rprint(f"[bold green]✅ Bot[/bold green] — {bot_data.get('username', '?')}#{bot_data.get('discriminator', '0')}")

        # Test guild access
        guild_resp = await client.get(f"{base}/guilds/{guild_id}", headers=headers)
        if guild_resp.status_code == 403:
            rprint(f"[bold red]❌ Guild[/bold red] — Bot is not a member of guild {guild_id} (403 Forbidden)")
            return
        if guild_resp.status_code == 404:
            rprint(f"[bold red]❌ Guild[/bold red] — Guild {guild_id} not found (404)")
            return
        guild_resp.raise_for_status()
        guild_name = guild_resp.json().get("name", "")
        rprint(f"[bold green]✅ Guild[/bold green] — {guild_name} ({guild_id})")

        # List voice channels
        channels_resp = await client.get(f"{base}/guilds/{guild_id}/channels", headers=headers)
        channels_resp.raise_for_status()
        voice_channels = [ch for ch in channels_resp.json() if ch.get("type") == 2]
        rprint(f"\n[bold]{len(voice_channels)}[/bold] voice channel(s):")
        for ch in voice_channels:
            rprint(f"  🔊 [cyan]{ch['name']}[/cyan] (id: {ch['id']})")

        # Check bot application intents
        app_resp = await client.get(f"{base}/oauth2/applications/@me", headers=headers)
        if app_resp.status_code == 200:
            app_data = app_resp.json()
            flags = app_data.get("flags", 0)
            # Bit 15 = GATEWAY_GUILD_MEMBERS, Bit 17 = GATEWAY_GUILD_MEMBERS_LIMITED
            # Bit 23 = GATEWAY_VOICE_STATES (not a flag — voice_states is non-privileged)
            has_members_intent = bool(flags & (1 << 15)) or bool(flags & (1 << 17))
            rprint("")
            rprint("[bold]Privileged intents:[/bold]")
            if has_members_intent:
                rprint("  ✅ GUILD_MEMBERS (privileged) — enabled, nicknames will be richer")
            else:
                rprint("  ℹ️  GUILD_MEMBERS (privileged) — not enabled (optional, nicknames come from voice events)")
            rprint("  ✅ GUILD_VOICE_STATES — non-privileged, always available")

    rprint("\n[dim]Note: voice state data (who is connected) requires the running backend server.[/dim]")


@discord_app.command("check")
def check() -> None:
    """Check Discord bot connectivity, guild access, and intents."""
    rprint("[bold]Connecting to Discord API...[/bold]")
    try:
        asyncio.run(_check())
    except Exception as e:
        rprint(f"[bold red]Error[/bold red] — {e}")
