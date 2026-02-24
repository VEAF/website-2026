import asyncio
import logging
from urllib.parse import parse_qs, urlparse

import ts3.query

from app.config import settings
from app.utils.cache import teamspeak_cache

logger = logging.getLogger(__name__)


def _parse_ts_url(url: str) -> dict:
    """Parse serverquery://host:port/?server_port=XXXX into components."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 10011,
        "server_port": int(params.get("server_port", [9987])[0]),
    }


def _fetch_ts_data_sync() -> dict:
    """Connect to TS3 ServerQuery and fetch clients/channels.

    Synchronous — must be called via asyncio.to_thread().
    Returns dict with clients, channels, client_count.
    """
    url_parts = _parse_ts_url(settings.API_TEAMSPEAK_URL)

    with ts3.query.TS3Connection(url_parts["host"], url_parts["port"]) as ts3conn:
        ts3conn.use(port=url_parts["server_port"])

        # Fetch clients
        try:
            raw_clients = ts3conn.clientlist()
        except ts3.query.TS3QueryError:
            raw_clients = None

        clients = []
        if raw_clients is not None:
            for c in raw_clients.parsed:
                nickname = c.get("client_nickname", "")
                # Filter out ServerQuery clients (client_type=1)
                if str(c.get("client_type", "0")) == "1":
                    continue
                # Filter out "Unknown" clients
                if nickname.startswith("Unknown"):
                    continue
                clients.append({
                    "clid": int(c.get("clid", 0)),
                    "cid": int(c.get("cid", 0)),
                    "nickname": nickname,
                })

        # Fetch channels
        try:
            raw_channels = ts3conn.channellist()
        except ts3.query.TS3QueryError:
            raw_channels = None

        channels = []
        if raw_channels is not None:
            for ch in raw_channels.parsed:
                cid = int(ch.get("cid", 0))
                channel_clients = [cl for cl in clients if cl["cid"] == cid]
                channels.append({
                    "cid": cid,
                    "pid": int(ch.get("pid", 0)),
                    "name": ch.get("channel_name", ""),
                    "clients": channel_clients,
                })

    return {
        "clients": clients,
        "channels": channels,
        "client_count": len(clients),
    }


async def scan_and_cache() -> None:
    """Fetch TS data in a thread and store in cache. Called by scheduler."""
    if not settings.API_TEAMSPEAK_URL:
        return
    try:
        data = await asyncio.to_thread(_fetch_ts_data_sync)
        teamspeak_cache["ts_status"] = data
        logger.info("TeamSpeak scan: %d clients, %d channels", data["client_count"], len(data["channels"]))
    except Exception:
        logger.exception("Failed to scan TeamSpeak server")


def get_cached_status() -> dict | None:
    """Read cached TS status. Returns None if cache is empty."""
    return teamspeak_cache.get("ts_status")


def get_client_count() -> int:
    """Read cached client count for header badge."""
    data = teamspeak_cache.get("ts_status")
    if data:
        return data.get("client_count", 0)
    return 0
