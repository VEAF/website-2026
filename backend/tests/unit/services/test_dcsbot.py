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
    monkeypatch.setattr(settings, "API_DCSSERVERBOT_URL", "https://dcs.example.org")
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


@pytest.mark.asyncio
async def test_api_key_not_sent_over_plain_http(monkeypatch: pytest.MonkeyPatch, captured: list[httpx.Request]):
    # GIVEN
    monkeypatch.setattr(settings, "API_DCSSERVERBOT_URL", "http://dcs.example.org:9876")
    monkeypatch.setattr(settings, "API_DCSSERVERBOT_KEY", SecretStr("test-key"))

    # WHEN
    await dcsbot.get_servers()

    # THEN
    assert len(captured) == 1
    assert "X-API-Key" not in captured[0].headers


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://dcs.example.org", True),
        ("http://127.0.0.1:9876", True),
        ("http://localhost:9876", True),
        ("http://192.168.1.10:9876", True),
        ("http://10.0.0.5:9876", True),
        ("http://dcs.example.org:9876", False),
        ("http://8.8.8.8:9876", False),
    ],
)
def test_can_send_api_key(url: str, expected: bool):
    # WHEN
    result = dcsbot.can_send_api_key(url)

    # THEN
    assert result is expected


@pytest.fixture
def bot_players(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    """Fake bot: two accounts share the name "Viper"; only ucid "u-mine" is ours."""
    requests: list[httpx.Request] = []
    rows = [
        {"ucid": "u-other", "discord_id": 2, "nick": "Viper", "date": "2026-10-10T20:00:00"},
        {"ucid": "u-mine", "discord_id": 1, "nick": "Viper", "date": "2026-10-01T20:00:00"},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        form = dict(httpx.QueryParams(request.content.decode()))
        if request.url.path.endswith("/getuser"):
            if "discord_id" in form:
                return httpx.Response(200, json=[r for r in rows if str(r["discord_id"]) == form["discord_id"]])
            return httpx.Response(200, json=[r for r in rows if form["nick"].lower() in r["nick"].lower()])
        if request.url.path.endswith("/stats"):
            return httpx.Response(200, json={"nick": form["nick"], "date": form["date"], "kills": 7})
        return httpx.Response(404)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        dcsbot.httpx, "AsyncClient", lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw)
    )
    dcsbot_cache.clear()
    yield requests
    dcsbot_cache.clear()


@pytest.mark.asyncio
async def test_player_stats_resolved_by_ucid_not_by_name(bot_players: list[httpx.Request]):
    # WHEN
    stats = await dcsbot.get_player_stats("u-mine", None, ("Viper",))

    # THEN
    assert stats == {"nick": "Viper", "date": "2026-10-01T20:00:00", "kills": 7}


@pytest.mark.asyncio
async def test_player_stats_tries_discord_id_first(bot_players: list[httpx.Request]):
    # WHEN
    stats = await dcsbot.get_player_stats("u-mine", "1", ("Viper",))

    # THEN
    assert stats["date"] == "2026-10-01T20:00:00"
    getuser_calls = [r for r in bot_players if r.url.path.endswith("/getuser")]
    assert len(getuser_calls) == 1
    assert "discord_id=1" in getuser_calls[0].content.decode()


@pytest.mark.asyncio
async def test_player_stats_none_when_account_unknown_to_bot(bot_players: list[httpx.Request]):
    # WHEN
    stats = await dcsbot.get_player_stats("u-absent", "3", ("Viper", "Ghost"))

    # THEN
    assert stats is None
    assert not any(r.url.path.endswith("/stats") for r in bot_players)
