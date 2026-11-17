import http.client
import socket

import pytest

from httpkit.server import build_response, parse_request, route


def fetch(port, method="GET", path="/", headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        conn.request(method, path, headers=headers or {})
        response = conn.getresponse()
        return response.status, response.read()
    finally:
        conn.close()


def raw_exchange(port, payload):
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(payload)
        return sock.recv(4096)


def test_parse_request():
    raw = b"GET /a HTTP/1.1\r\nHost: x\r\nUser-Agent: curl\r\n\r\n"
    assert parse_request(raw) == ("GET", "/a", {"host": "x", "user-agent": "curl"})


@pytest.mark.parametrize("raw", [b"", b"GARBAGE", b"GET /\r\n\r\n"])
def test_parse_request_rejects_malformed(raw):
    with pytest.raises(ValueError):
        parse_request(raw)


@pytest.mark.parametrize(
    "method, path, expected",
    [
        ("GET", "/", 200),
        ("GET", "/echo/hi?x=1", 200),
        ("GET", "/missing", 404),
        ("GET", "/echo", 404),
        ("POST", "/", 405),
    ],
)
def test_route_status(method, path, expected):
    assert route(method, path, {})[0] == expected


def test_build_response():
    raw = build_response(404, "no")
    assert raw.startswith(b"HTTP/1.1 404 Not Found\r\n")
    assert b"Content-Length: 2\r\n" in raw
    assert raw.endswith(b"\r\n\r\nno")


def test_root_echo_and_user_agent_over_a_real_socket(server):
    assert fetch(server) == (200, b"tiny-http-toolkit is running")
    assert fetch(server, path="/echo/hello%20world") == (200, b"hello world")
    assert fetch(server, path="/user-agent", headers={"User-Agent": "t"}) == (200, b"t")


def test_unknown_path_and_method(server):
    assert fetch(server, path="/nope")[0] == 404
    assert fetch(server, "POST", "/")[0] == 405


def test_malformed_request_gets_400(server):
    assert raw_exchange(server, b"NONSENSE\r\n\r\n").startswith(b"HTTP/1.1 400")


def test_silent_client_does_not_block_the_server(server):
    with socket.create_connection(("127.0.0.1", server)):
        assert fetch(server)[0] == 200
