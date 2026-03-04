from unittest.mock import MagicMock, patch

import pytest

from app.services.ts3_client import TS3Connection, TS3QueryError, parse_ts3_response, ts3_unescape


class TestTs3Unescape:
    def test_space(self):
        assert ts3_unescape(r"Hello\sWorld") == "Hello World"

    def test_slash(self):
        assert ts3_unescape(r"foo\/bar") == "foo/bar"

    def test_pipe(self):
        assert ts3_unescape(r"foo\pbar") == "foo|bar"

    def test_backslash(self):
        assert ts3_unescape("foo\\\\bar") == "foo\\bar"

    def test_tab(self):
        assert ts3_unescape(r"foo\tbar") == "foo\tbar"

    def test_combined(self):
        assert ts3_unescape(r"Hello\sWorld\s\/\sfoo") == "Hello World / foo"

    def test_no_escaping_needed(self):
        assert ts3_unescape("plain_text") == "plain_text"

    def test_empty_string(self):
        assert ts3_unescape("") == ""


class TestParseTs3Response:
    def test_single_item(self):
        # GIVEN
        line = "clid=5 cid=7 client_nickname=ScP client_type=0"

        # WHEN
        result = parse_ts3_response(line)

        # THEN
        assert len(result) == 1
        assert result[0]["clid"] == "5"
        assert result[0]["cid"] == "7"
        assert result[0]["client_nickname"] == "ScP"
        assert result[0]["client_type"] == "0"

    def test_multiple_items(self):
        # GIVEN
        line = "clid=5 cid=7|clid=6 cid=8"

        # WHEN
        result = parse_ts3_response(line)

        # THEN
        assert len(result) == 2
        assert result[0]["clid"] == "5"
        assert result[1]["clid"] == "6"

    def test_escaped_values(self):
        # GIVEN
        line = r"channel_name=Default\sChannel"

        # WHEN
        result = parse_ts3_response(line)

        # THEN
        assert result[0]["channel_name"] == "Default Channel"

    def test_empty_line(self):
        assert parse_ts3_response("") == []

    def test_whitespace_only(self):
        assert parse_ts3_response("   ") == []

    def test_key_without_value(self):
        # GIVEN
        line = "flagkey"

        # WHEN
        result = parse_ts3_response(line)

        # THEN
        assert result[0]["flagkey"] == ""

    def test_value_containing_equals(self):
        # GIVEN — e.g. client_unique_identifier=abc123==
        line = "uid=abc123=="

        # WHEN
        result = parse_ts3_response(line)

        # THEN
        assert result[0]["uid"] == "abc123=="


class TestTS3Connection:
    def _make_connection(self, recv_data: list[bytes]) -> TS3Connection:
        """Create a TS3Connection with a mocked socket."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = recv_data

        conn = TS3Connection.__new__(TS3Connection)
        conn._sock = mock_sock
        conn._buffer = b""
        conn._host = "localhost"
        conn._port = 10011
        conn._timeout = 10.0
        return conn

    def test_send_command_parses_data(self):
        # GIVEN
        conn = self._make_connection([
            b"clid=1 cid=10 client_nickname=Pilot1 client_type=0|clid=2 cid=20 client_nickname=Pilot2 client_type=0\n\r",
            b"error id=0 msg=ok\n\r",
        ])

        # WHEN
        result = conn.clientlist()

        # THEN
        assert len(result) == 2
        assert result[0]["client_nickname"] == "Pilot1"
        assert result[1]["client_nickname"] == "Pilot2"

    def test_send_command_handles_error(self):
        # GIVEN
        conn = self._make_connection([
            b"error id=1281 msg=database\\sempty\\sresult\\sset\n\r",
        ])

        # WHEN / THEN
        with pytest.raises(TS3QueryError) as exc_info:
            conn.clientlist()
        assert exc_info.value.error_id == "1281"
        assert exc_info.value.error_msg == "database empty result set"

    def test_use_command(self):
        # GIVEN
        conn = self._make_connection([
            b"error id=0 msg=ok\n\r",
        ])

        # WHEN — should not raise
        conn.use(port=9987)

        # THEN
        conn._sock.sendall.assert_called_with(b"use port=9987\n\r")

    def test_chunked_response(self):
        # GIVEN — data arrives in small chunks, marker split across chunks
        conn = self._make_connection([
            b"clid=1 cid=10\n",
            b"\r",
            b"error id=0 msg=ok\n\r",
        ])

        # WHEN
        result = conn.clientlist()

        # THEN
        assert len(result) == 1
        assert result[0]["clid"] == "1"

    @patch("app.services.ts3_client.socket.create_connection")
    def test_connect_reads_banner(self, mock_create_conn):
        # GIVEN
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            b"TS3\n\r",
            b"Welcome to the TeamSpeak 3 ServerQuery interface.\n\r",
        ]
        mock_create_conn.return_value = mock_sock

        # WHEN
        conn = TS3Connection("localhost", 10011)
        conn._connect()

        # THEN
        assert conn._sock is mock_sock
        assert mock_sock.recv.call_count == 2

    def test_close_sends_quit(self):
        # GIVEN
        mock_sock = MagicMock()
        conn = TS3Connection.__new__(TS3Connection)
        conn._sock = mock_sock

        # WHEN
        conn._close()

        # THEN
        mock_sock.sendall.assert_called_with(b"quit\n\r")
        mock_sock.close.assert_called_once()
        assert conn._sock is None

    def test_close_handles_socket_error(self):
        # GIVEN
        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = OSError("broken pipe")
        conn = TS3Connection.__new__(TS3Connection)
        conn._sock = mock_sock

        # WHEN — should not raise
        conn._close()

        # THEN
        mock_sock.close.assert_called_once()
        assert conn._sock is None

    def test_connection_closed_raises(self):
        # GIVEN — socket returns empty bytes (connection closed)
        conn = self._make_connection([b""])

        # WHEN / THEN
        with pytest.raises(ConnectionError, match="closed unexpectedly"):
            conn.clientlist()
