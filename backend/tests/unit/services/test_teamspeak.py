from unittest.mock import MagicMock, patch

from app.services.teamspeak import _fetch_ts_data_sync, _parse_ts_url, get_cached_status, get_client_count
from app.utils.cache import teamspeak_cache


class TestParseUrl:
    def test_parses_standard_url(self):
        # GIVEN
        url = "serverquery://ts.veaf.org:10011/?server_port=9987"

        # WHEN
        result = _parse_ts_url(url)

        # THEN
        assert result["host"] == "ts.veaf.org"
        assert result["port"] == 10011
        assert result["server_port"] == 9987

    def test_parses_url_with_defaults(self):
        # GIVEN
        url = "serverquery://localhost"

        # WHEN
        result = _parse_ts_url(url)

        # THEN
        assert result["host"] == "localhost"
        assert result["port"] == 10011
        assert result["server_port"] == 9987

    def test_parses_custom_ports(self):
        # GIVEN
        url = "serverquery://myserver:20011/?server_port=10987"

        # WHEN
        result = _parse_ts_url(url)

        # THEN
        assert result["host"] == "myserver"
        assert result["port"] == 20011
        assert result["server_port"] == 10987


class TestGetClientCount:
    def setup_method(self):
        teamspeak_cache.clear()

    def test_returns_zero_when_cache_empty(self):
        # GIVEN — empty cache

        # WHEN
        result = get_client_count()

        # THEN
        assert result == 0

    def test_returns_count_from_cache(self):
        # GIVEN
        teamspeak_cache["ts_status"] = {"client_count": 5, "clients": [], "channels": []}

        # WHEN
        result = get_client_count()

        # THEN
        assert result == 5


class TestGetCachedStatus:
    def setup_method(self):
        teamspeak_cache.clear()

    def test_returns_none_when_cache_empty(self):
        # GIVEN — empty cache

        # WHEN
        result = get_cached_status()

        # THEN
        assert result is None

    def test_returns_data_from_cache(self):
        # GIVEN
        data = {"client_count": 3, "clients": [{"clid": 1, "cid": 1, "nickname": "Test"}], "channels": []}
        teamspeak_cache["ts_status"] = data

        # WHEN
        result = get_cached_status()

        # THEN
        assert result == data
        assert result["client_count"] == 3


class TestFetchTsDataSync:
    @patch("app.services.teamspeak.ts3.query.TS3Connection")
    @patch("app.services.teamspeak.settings")
    def test_fetches_and_filters_clients(self, mock_settings, mock_ts3_class):
        # GIVEN
        mock_settings.API_TEAMSPEAK_URL = "serverquery://ts.veaf.org:10011/?server_port=9987"

        mock_conn = MagicMock()
        mock_ts3_class.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_ts3_class.return_value.__exit__ = MagicMock(return_value=False)

        mock_conn.clientlist.return_value.parsed = [
            {"clid": "1", "cid": "10", "client_nickname": "Pilot1", "client_type": "0"},
            {"clid": "2", "cid": "10", "client_nickname": "Unknown from 1.2.3.4", "client_type": "0"},
            {"clid": "3", "cid": "20", "client_nickname": "ServerQuery", "client_type": "1"},
            {"clid": "4", "cid": "20", "client_nickname": "Pilot2", "client_type": "0"},
        ]
        mock_conn.channellist.return_value.parsed = [
            {"cid": "10", "pid": "0", "channel_name": "Lobby"},
            {"cid": "20", "pid": "0", "channel_name": "Ops Room"},
        ]

        # WHEN
        result = _fetch_ts_data_sync()

        # THEN
        assert result["client_count"] == 2
        assert len(result["clients"]) == 2
        assert result["clients"][0]["nickname"] == "Pilot1"
        assert result["clients"][1]["nickname"] == "Pilot2"

        # Verify channel-client mapping
        lobby = next(ch for ch in result["channels"] if ch["name"] == "Lobby")
        assert len(lobby["clients"]) == 1
        assert lobby["clients"][0]["nickname"] == "Pilot1"

        ops = next(ch for ch in result["channels"] if ch["name"] == "Ops Room")
        assert len(ops["clients"]) == 1
        assert ops["clients"][0]["nickname"] == "Pilot2"

    @patch("app.services.teamspeak.ts3.query.TS3Connection")
    @patch("app.services.teamspeak.settings")
    def test_empty_server(self, mock_settings, mock_ts3_class):
        # GIVEN
        mock_settings.API_TEAMSPEAK_URL = "serverquery://ts.veaf.org:10011/?server_port=9987"

        mock_conn = MagicMock()
        mock_ts3_class.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_ts3_class.return_value.__exit__ = MagicMock(return_value=False)

        mock_conn.clientlist.return_value.parsed = []
        mock_conn.channellist.return_value.parsed = [
            {"cid": "1", "pid": "0", "channel_name": "Default Channel"},
        ]

        # WHEN
        result = _fetch_ts_data_sync()

        # THEN
        assert result["client_count"] == 0
        assert len(result["clients"]) == 0
        assert len(result["channels"]) == 1
        assert result["channels"][0]["clients"] == []
