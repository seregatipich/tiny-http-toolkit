"""Minimal HTTP/1.1 server on plain sockets: ``/``, ``/echo/<text>`` and ``/user-agent``."""

import socket
import threading
from contextlib import suppress
from http import HTTPStatus
from urllib.parse import unquote, urlsplit


def read_request_bytes(
    client_connection: socket.socket, max_request_bytes: int = 8192
) -> bytes:
    """Read from ``client_connection`` until the blank line that ends the headers.

    Stops early if the client closes the connection.

    Raises:
        ValueError: if the headers are not finished within ``max_request_bytes``.
        OSError: on network errors, including a timeout.
    """
    request_bytes = b""
    while b"\r\n\r\n" not in request_bytes:
        if len(request_bytes) >= max_request_bytes:
            raise ValueError("Request headers are too large.")
        received_bytes = client_connection.recv(4096)
        if not received_bytes:
            break
        request_bytes += received_bytes
    return request_bytes


def parse_request(request_bytes: bytes) -> tuple[str, str, dict]:
    """Return ``(http_method, path, headers)`` from the bytes of a request.

    Header names are lower-cased.

    Raises:
        ValueError: if the request line is not ``METHOD PATH VERSION``.
    """
    request_lines = request_bytes.decode("latin-1").split("\r\n")
    request_line_parts = request_lines[0].split(" ")
    if len(request_line_parts) != 3:
        raise ValueError("Malformed request line.")
    http_method, path, _http_version = request_line_parts
    headers = {}
    for header_line in request_lines[1:]:
        header_name, separator, header_value = header_line.partition(":")
        if separator:
            headers[header_name.strip().lower()] = header_value.strip()
    return http_method, path, headers


def choose_response(http_method: str, path: str, headers: dict) -> tuple[int, str]:
    """Return ``(status_code, response_text)`` for a parsed request."""
    path_without_query = urlsplit(path).path
    if http_method != "GET":
        return 405, "Method not allowed"
    if path_without_query == "/":
        return 200, "tiny-http-toolkit is running"
    if path_without_query == "/user-agent":
        return 200, headers.get("user-agent", "")
    echo_prefix = "/echo/"
    if path_without_query.startswith(echo_prefix):
        return 200, unquote(path_without_query[len(echo_prefix) :])
    return 404, "Not found"


def build_http_response(status_code: int, response_text: str) -> bytes:
    """Serialise a plain-text HTTP response."""
    body = response_text.encode("utf-8")
    head = (
        f"HTTP/1.1 {status_code} {HTTPStatus(status_code).phrase}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "X-Content-Type-Options: nosniff\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode("latin-1") + body


def answer_client(client_connection: socket.socket) -> None:
    """Answer one request on ``client_connection`` and close it.

    Malformed or oversized requests get 400; clients that stay silent for a second
    are dropped.
    """
    silent_client_timeout_seconds = 1
    with client_connection:
        client_connection.settimeout(silent_client_timeout_seconds)
        try:
            request_bytes = read_request_bytes(client_connection)
            status_code, response_text = choose_response(*parse_request(request_bytes))
        except ValueError:
            status_code, response_text = 400, "Bad request"
        except OSError:
            return
        with suppress(OSError):
            client_connection.sendall(build_http_response(status_code, response_text))


def serve_clients(listening_socket: socket.socket) -> None:
    """Answer clients one after another until ``listening_socket`` is closed."""
    while True:
        try:
            client_connection, _client_address = listening_socket.accept()
        except OSError:
            return
        answer_client(client_connection)


def start_server(host: str, port: int) -> socket.socket:
    """Listen on ``host:port`` (port 0 picks a free one) in a background thread.

    Returns the listening socket: ``getsockname()[1]`` is the real port and
    ``close()`` stops the server.

    Raises:
        OSError: if the address cannot be bound.
    """
    listening_socket = socket.create_server((host, port))
    threading.Thread(
        target=serve_clients, args=(listening_socket,), daemon=True
    ).start()
    return listening_socket
