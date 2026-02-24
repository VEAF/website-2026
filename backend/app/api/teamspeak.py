from urllib.parse import urlparse

from fastapi import APIRouter

from app.config import settings
from app.schemas.teamspeak import TSChannelOut, TSClientOut, TSStatusOut
from app.services import teamspeak as ts_service

router = APIRouter(prefix="/teamspeak", tags=["teamspeak"])


@router.get("/status", response_model=TSStatusOut)
async def get_teamspeak_status():
    if not settings.API_TEAMSPEAK_URL:
        return TSStatusOut(clients=[], channels=[], client_count=0, server_host="", configured=False)

    data = ts_service.get_cached_status()
    parsed_url = urlparse(settings.API_TEAMSPEAK_URL)
    server_host = parsed_url.hostname or ""

    if data is None:
        return TSStatusOut(clients=[], channels=[], client_count=0, server_host=server_host, configured=True)

    clients = [TSClientOut(**c) for c in data["clients"]]
    channels = [
        TSChannelOut(
            cid=ch["cid"],
            pid=ch["pid"],
            name=ch["name"],
            clients=[TSClientOut(**c) for c in ch["clients"]],
        )
        for ch in data["channels"]
    ]

    return TSStatusOut(
        clients=clients,
        channels=channels,
        client_count=data["client_count"],
        server_host=server_host,
        configured=True,
    )
