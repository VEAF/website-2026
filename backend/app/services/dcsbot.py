import ipaddress
import logging
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.utils.cache import cached, dcsbot_cache

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # seconds


def can_send_api_key(url: str) -> bool:
    """The API key may only travel over HTTPS, or to a loopback or private address."""
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return True
    if parsed.hostname == "localhost":
        return True
    try:
        address = ipaddress.ip_address(parsed.hostname or "")
    except ValueError:
        return False
    return address.is_loopback or address.is_private


def _client() -> httpx.AsyncClient:
    """HTTP client for the bot REST API, sending the API key when one is configured."""
    api_key = settings.API_DCSSERVERBOT_KEY.get_secret_value()
    headers = {}
    if api_key:
        if can_send_api_key(settings.API_DCSSERVERBOT_URL):
            headers["X-API-Key"] = api_key
        else:
            logger.warning("API_DCSSERVERBOT_KEY is set but not sent: API_DCSSERVERBOT_URL is not https")
    return httpx.AsyncClient(timeout=TIMEOUT, headers=headers)


@cached(dcsbot_cache)
async def get_servers() -> list[dict] | None:
    """Fetch servers list from DCSServerBot API."""
    try:
        async with _client() as client:
            resp = await client.get(f"{settings.API_DCSSERVERBOT_URL}/serverapi/servers")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot servers")
        return None


@cached(dcsbot_cache)
async def get_server_stats() -> dict | None:
    """Fetch global server statistics from DCSServerBot API."""
    try:
        async with _client() as client:
            resp = await client.get(f"{settings.API_DCSSERVERBOT_URL}/serverapi/serverstats")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot server stats")
        return None


@cached(dcsbot_cache)
async def get_server(server_name: str) -> list[dict] | None:
    """Fetch a specific server from DCSServerBot API by server_name."""
    try:
        async with _client() as client:
            resp = await client.get(
                f"{settings.API_DCSSERVERBOT_URL}/serverapi/servers",
                params={"server_name": server_name},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot server %s", server_name)
        return None


@cached(dcsbot_cache)
async def get_server_stats_by_name(server_name: str) -> dict | None:
    """Fetch server-specific statistics from DCSServerBot API."""
    try:
        async with _client() as client:
            resp = await client.get(
                f"{settings.API_DCSSERVERBOT_URL}/serverapi/serverstats",
                params={"server_name": server_name},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot stats for %s", server_name)
        return None


@cached(dcsbot_cache)
async def get_server_attendance(server_name: str) -> dict | None:
    """Fetch server attendance from DCSServerBot API."""
    try:
        async with _client() as client:
            resp = await client.get(
                f"{settings.API_DCSSERVERBOT_URL}/serverapi/server_attendance",
                params={"server_name": server_name},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot attendance for %s", server_name)
        return None


@cached(dcsbot_cache)
async def get_player_stats(ucid: str, discord_id: str | None, nicknames: tuple[str, ...]) -> dict | None:
    """Fetch the game statistics of one DCS account from DCSServerBot API.

    The bot's /stats only takes a (nick, date) pair, which it resolves to the account last seen under that
    name at that second. That pair is read from /getuser (by Discord id first, then by nickname), keeping
    only the row of this ucid, so a player using someone else's name never gets their statistics.
    """
    lookups = ([{"discord_id": discord_id}] if discord_id else []) + [{"nick": n} for n in nicknames if n]
    try:
        async with _client() as client:
            for form in lookups:
                resp = await client.post(f"{settings.API_DCSSERVERBOT_URL}/serverapi/getuser", data=form)
                resp.raise_for_status()
                entry = next((e for e in resp.json() if e.get("ucid") == ucid), None)
                if entry is None:
                    continue
                resp = await client.post(
                    f"{settings.API_DCSSERVERBOT_URL}/serverapi/stats",
                    data={"nick": entry["nick"], "date": entry["date"]},
                )
                resp.raise_for_status()
                return resp.json()
        return None
    except Exception:
        logger.exception("Failed to fetch DCSServerBot stats for player %s", ucid)
        return None
