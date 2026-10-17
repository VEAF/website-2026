import logging

import httpx

from app.config import settings
from app.utils.cache import cached, dcsbot_cache

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # seconds


def _client() -> httpx.AsyncClient:
    """HTTP client for the bot REST API, sending the API key when one is configured."""
    api_key = settings.API_DCSSERVERBOT_KEY.get_secret_value()
    headers = {"X-API-Key": api_key} if api_key else {}
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
