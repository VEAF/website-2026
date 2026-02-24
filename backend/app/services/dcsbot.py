import logging

import httpx

from app.config import settings
from app.utils.cache import cached, dcsbot_cache

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # seconds


@cached(dcsbot_cache)
async def get_servers() -> list[dict] | None:
    """Fetch servers list from DCSServerBot API."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
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
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{settings.API_DCSSERVERBOT_URL}/serverapi/serverstats")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch DCSServerBot server stats")
        return None
