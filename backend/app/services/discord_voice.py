import asyncio
import logging
from threading import Thread

import discord

from app.config import settings
from app.utils.cache import discord_voice_cache

logger = logging.getLogger(__name__)

_monitor: "DiscordVoiceMonitor | None" = None


class DiscordVoiceMonitor:
    """Discord Gateway bot that tracks voice channel presence in a background thread.

    Does NOT require the privileged GUILD_MEMBERS intent.
    Voice state data (including member info) is provided by the GUILD_VOICE_STATES intent
    through the READY payload and on_voice_state_update events.
    """

    def __init__(self, token: str, guild_id: str):
        self._token = token
        self._guild_id = int(guild_id)
        self._thread: Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

        # Track voice states manually: {user_id: {channel_id, nickname, bot}}
        self._voice_states: dict[int, dict] = {}

        intents = discord.Intents.default()
        intents.voice_states = True
        intents.members = False  # Privileged — not required
        self._client = discord.Client(intents=intents)

        @self._client.event
        async def on_ready():
            logger.info("🤖 Discord bot connected as %s", self._client.user)
            # READY payload includes voice states for all guilds the bot is in.
            # discord.py populates guild.voice_channels[].voice_states from this.
            self._build_initial_state()
            self._update_cache()

        @self._client.event
        async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
            if member.guild.id != self._guild_id:
                return

            if after.channel is None:
                # User left voice
                self._voice_states.pop(member.id, None)
            else:
                # User joined or moved
                self._voice_states[member.id] = {
                    "channel_id": after.channel.id,
                    "nickname": member.nick or member.global_name or member.name or "Inconnu",
                    "bot": member.bot,
                }

            self._update_cache()

    def _build_initial_state(self) -> None:
        """Build voice state map from the guild's current voice channels (READY payload)."""
        guild = self._client.get_guild(self._guild_id)
        if not guild:
            logger.warning("Discord guild %s not found in bot cache", self._guild_id)
            return

        self._voice_states.clear()
        for vc in guild.voice_channels:
            for vs in vc.voice_states:
                # vs is a VoiceState; vs.channel is set, member may be partial
                member = guild.get_member(vs.member.id) if vs.member else None
                if member is None and vs.member:
                    member = vs.member
                if member is None:
                    continue
                self._voice_states[member.id] = {
                    "channel_id": vc.id,
                    "nickname": member.nick or member.global_name or member.name or "Inconnu",
                    "bot": member.bot,
                }

    def _update_cache(self) -> None:
        """Rebuild the cache dict from tracked voice states."""
        guild = self._client.get_guild(self._guild_id)
        guild_name = guild.name if guild else ""

        # Group users by channel
        channel_users: dict[int, list[dict]] = {}
        all_users: list[dict] = []

        for user_id, state in list(self._voice_states.items()):
            if state["bot"]:
                continue
            user_dict = {"user_id": str(user_id), "nickname": state["nickname"]}
            all_users.append(user_dict)
            channel_users.setdefault(state["channel_id"], []).append(user_dict)

        # Build channel list with names
        channels: list[dict] = []
        if guild:
            for vc in guild.voice_channels:
                users_in_ch = channel_users.get(vc.id, [])
                channels.append({
                    "channel_id": str(vc.id),
                    "name": vc.name,
                    "users": users_in_ch,
                })

        discord_voice_cache["discord_voice_status"] = {
            "users": all_users,
            "channels": channels,
            "user_count": len(all_users),
            "guild_name": guild_name,
        }
        logger.info("🤖 Discord voice cache updated: %d user(s), %d channel(s)", len(all_users), len(channels))

    def _run(self) -> None:
        """Entry point for the background thread — runs the bot's event loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._client.start(self._token))
        except discord.PrivilegedIntentsRequired:
            logger.error(
                "❌ Discord bot failed: privileged intents not enabled in Developer Portal. "
                "Go to https://discord.com/developers/applications/ and enable GUILD_MEMBERS intent, "
                "or the bot will run without it (nicknames may be less accurate)."
            )
        except discord.LoginFailure:
            logger.error("❌ Discord bot failed: invalid DISCORD_BOT_TOKEN")
        except Exception:
            logger.exception("❌ Discord bot crashed")
        finally:
            self._loop.close()

    def start(self) -> None:
        """Start the bot in a daemon background thread."""
        self._thread = Thread(target=self._run, daemon=True, name="discord-voice-bot")
        self._thread.start()
        logger.info("Discord voice monitor started (guild_id=%s)", self._guild_id)

    async def stop(self) -> None:
        """Gracefully close the bot from the main thread."""
        if self._client and self._loop and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._client.close(), self._loop)
            try:
                future.result(timeout=10)
            except Exception:
                logger.exception("Error closing Discord bot")
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Discord voice monitor stopped")


# ---------------------------------------------------------------------------
# Public API (signatures unchanged for backward compatibility)
# ---------------------------------------------------------------------------


def start_monitor() -> None:
    """Create and start the Discord voice monitor bot."""
    global _monitor
    if _monitor is not None:
        return
    _monitor = DiscordVoiceMonitor(settings.DISCORD_BOT_TOKEN, settings.DISCORD_GUILD_ID)
    _monitor.start()


async def stop_monitor() -> None:
    """Stop the Discord voice monitor bot."""
    global _monitor
    if _monitor:
        await _monitor.stop()
        _monitor = None


def get_cached_status() -> dict | None:
    """Read cached Discord voice status. Returns None if cache is empty."""
    return discord_voice_cache.get("discord_voice_status")


def get_user_count() -> int:
    """Read cached user count for header badge."""
    data = discord_voice_cache.get("discord_voice_status")
    if data:
        return data.get("user_count", 0)
    return 0
