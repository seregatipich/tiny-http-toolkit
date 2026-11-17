"""Minimal HTTP/1.1 server on plain sockets: ``/``, ``/echo/<text>`` and ``/user-agent``."""

import socket
import threading
from contextlib import suppress
from http import HTTPStatus
from urllib.parse import unquote, urlsplit


def parse_request(raw: bytes) -> tuple[str, str, dict]:
    """Return ``(method, path, headers)`` from raw request bytes.

    Header names are lower-cased.

    Raises:
        ValueError: if the request line is malformed.
    """
    lines = raw.decode("latin-1").split("\r\n")
    parts = lines[0].split(" ")
    if len(parts) != 3:
        raise ValueError("Malformed request line.")
    headers = {}
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if sep:
            headers[name.strip().lower()] = value.strip()
    return parts[0], parts[1], headers


def route(method: str, path: str, headers: dict) -> tuple[int, str]:
    """Return ``(status, text)`` for a request."""
    path = urlsplit(path).path
    if method != "GET":
        return 405, "Method not allowed"
    if path == "/":
        return 200, "tiny-http-toolkit is running"
    if path == "/user-agent":
        return 200, headers.get("user-agent", "")
    if path.startswith("/echo/"):
        return 200, unquote(path[len("/echo/") :])
    return 404, "Not found"


def build_response(status: int, text: str) -> bytes:
    """Serialise a plain-text response."""
    body = text.encode("utf-8")
    head = (
        f"HTTP/1.1 {status} {HTTPStatus(status).phrase}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode("latin-1") + body


def handle_client(conn: socket.socket) -> None:
    """Answer one request on ``conn`` and close it.

    Malformed requests get 400; clients that stay silent for a second are dropped.
    """
    with conn:
        conn.settimeout(1)
        try:
            status, text = route(*parse_request(conn.recv(4096)))
        except ValueError:
            status, text = 400, "Bad request"
        except OSError:
            return
        with suppress(OSError):
            conn.sendall(build_response(status, text))


def serve(sock: socket.socket) -> None:
    """Handle clients one after another until ``sock`` is closed."""
    while True:
        try:
            conn, _ = sock.accept()
        except OSError:
            return
        handle_client(conn)


def start_server(host: str, port: int) -> socket.socket:
    """Listen on ``host:port`` (port 0 picks a free one) in a background thread.

    Returns the listening socket: ``getsockname()[1]`` is the real port and
    ``close()`` stops the server.

    Raises:
        OSError: if the address cannot be bound.
    """
    sock = socket.create_server((host, port))
    threading.Thread(target=serve, args=(sock,), daemon=True).start()
    return sock
