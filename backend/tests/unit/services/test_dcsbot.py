import httpx
import pytest
from pydantic import SecretStr

from app.config import settings
from app.services import dcsbot
from app.utils.cache import dcsbot_cache


@pytest.fixture
def captured(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    """Route the bot client to an in-memory transport and record the requests it sends."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[])

    real_client = httpx.AsyncClient

    def fake_client(**kwargs) -> httpx.AsyncClient:
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(dcsbot.httpx, "AsyncClient", fake_client)
    dcsbot_cache.clear()
    yield requests
    dcsbot_cache.clear()


@pytest.mark.asyncio
async def test_sends_api_key_header_when_configured(monkeypatch: pytest.MonkeyPatch, captured: list[httpx.Request]):
    # GIVEN
    monkeypatch.setattr(settings, "API_DCSSERVERBOT_KEY", SecretStr("test-key"))

    # WHEN
    await dcsbot.get_servers()
    await dcsbot.get_server_attendance("srv")

    # THEN
    assert len(captured) == 2
    assert all(r.headers.get("X-API-Key") == "test-key" for r in captured)


@pytest.mark.asyncio
async def test_no_api_key_header_when_not_configured(monkeypatch: pytest.MonkeyPatch, captured: list[httpx.Request]):
    # GIVEN
    monkeypatch.setattr(settings, "API_DCSSERVERBOT_KEY", SecretStr(""))

    # WHEN
    await dcsbot.get_server_stats()

    # THEN
    assert len(captured) == 1
    assert "X-API-Key" not in captured[0].headers
