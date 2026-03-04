"""Minimal TeamSpeak 3 ServerQuery client using raw TCP sockets.

Replaces the deprecated `ts3` library which depended on `telnetlib`
(removed in Python 3.13). Only implements the commands we need:
`use`, `clientlist`, `channellist`.

Protocol reference: TS3 ServerQuery uses plain text over TCP with
`\\n\\r` line endings. Responses contain key=value pairs with TS3
escaping, items separated by `|`.
"""

import re
import socket

# Single-pass unescape via regex to avoid issues with overlapping patterns
# (e.g. `\\b` must become `\b` literal, not backspace)
_UNESCAPE_TABLE = {
    "\\": "\\",
    "/": "/",
    "s": " ",
    "p": "|",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
}
_UNESCAPE_RE = re.compile(r"\\([\\\/spabfnrtv])")


class TS3QueryError(Exception):
    """Raised when the TS3 ServerQuery returns a non-zero error code."""

    def __init__(self, error_id: str, error_msg: str):
        self.error_id = error_id
        self.error_msg = error_msg
        super().__init__(f"TS3 error id={error_id} msg={error_msg}")


def ts3_unescape(value: str) -> str:
    """Unescape a TS3 ServerQuery value string."""
    return _UNESCAPE_RE.sub(lambda m: _UNESCAPE_TABLE[m.group(1)], value)


def parse_ts3_response(line: str) -> list[dict[str, str]]:
    """Parse a TS3 ServerQuery response data line into a list of dicts.

    Items separated by `|`, properties by spaces, key=value by `=`.
    """
    line = line.strip()
    if not line:
        return []
    items = line.split("|")
    result = []
    for item in items:
        props = {}
        for pair in item.split():
            parts = pair.split("=", 1)
            key = ts3_unescape(parts[0])
            val = ts3_unescape(parts[1]) if len(parts) > 1 else ""
            props[key] = val
        result.append(props)
    return result


class TS3Connection:
    """Minimal TeamSpeak 3 ServerQuery client using raw TCP sockets.

    Usage::

        with TS3Connection("ts.example.org", 10011) as conn:
            conn.use(port=9987)
            clients = conn.clientlist()
            channels = conn.channellist()
    """

    def __init__(self, host: str, port: int = 10011, timeout: float = 10.0):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._sock: socket.socket | None = None
        self._buffer = b""

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        return False

    def _connect(self):
        self._sock = socket.create_connection((self._host, self._port), timeout=self._timeout)
        self._sock.settimeout(self._timeout)
        # Read and discard the two welcome banner lines
        self._read_line()  # "TS3"
        self._read_line()  # "Welcome to the TeamSpeak 3 ServerQuery interface..."

    def _close(self):
        if self._sock:
            try:
                self._sock.sendall(b"quit\n\r")
            except OSError:
                pass
            finally:
                self._sock.close()
                self._sock = None

    def _read_line(self) -> bytes:
        """Read from socket until \\n\\r marker. Returns raw bytes."""
        marker = b"\n\r"
        while marker not in self._buffer:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("TS3 connection closed unexpectedly")
            self._buffer += chunk
        idx = self._buffer.index(marker) + len(marker)
        line = self._buffer[:idx]
        self._buffer = self._buffer[idx:]
        return line

    def _send_command(self, command: str) -> list[dict[str, str]]:
        """Send a command and return parsed response data."""
        self._sock.sendall(f"{command}\n\r".encode("utf-8"))

        data_lines = []
        while True:
            raw_line = self._read_line()
            line_str = raw_line.decode("utf-8", errors="ignore").strip("\n\r")
            if line_str.startswith("error "):
                # Parse: "error id=N msg=..."
                error_props = {}
                for pair in line_str[6:].split():
                    parts = pair.split("=", 1)
                    key = parts[0]
                    val = ts3_unescape(parts[1]) if len(parts) > 1 else ""
                    error_props[key] = val
                if error_props.get("id", "0") != "0":
                    raise TS3QueryError(
                        error_id=error_props.get("id", "?"),
                        error_msg=error_props.get("msg", "unknown"),
                    )
                break
            else:
                data_lines.append(line_str)

        result = []
        for dl in data_lines:
            result.extend(parse_ts3_response(dl))
        return result

    def use(self, *, port: int) -> None:
        """Select a virtual server by port."""
        self._send_command(f"use port={port}")

    def clientlist(self) -> list[dict[str, str]]:
        """Get list of connected clients."""
        return self._send_command("clientlist")

    def channellist(self) -> list[dict[str, str]]:
        """Get list of channels."""
        return self._send_command("channellist")
