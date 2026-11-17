import http.client
import socket

import pytest

from httpkit.server import build_http_response, choose_response, parse_request


def get_response(port, http_method="GET", path="/", headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(http_method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def send_raw_bytes(port, request_bytes):
    with socket.create_connection(("127.0.0.1", port), timeout=5) as client_socket:
        client_socket.sendall(request_bytes)
        return client_socket.recv(4096)


def test_parse_request_returns_method_path_and_lowercase_headers():
    request_bytes = b"GET /a HTTP/1.1\r\nHost: x\r\nUser-Agent: curl\r\n\r\n"
    assert parse_request(request_bytes) == (
        "GET",
        "/a",
        {"host": "x", "user-agent": "curl"},
    )


@pytest.mark.parametrize("request_bytes", [b"", b"GARBAGE", b"GET /\r\n\r\n"])
def test_parse_request_rejects_malformed_request_lines(request_bytes):
    with pytest.raises(ValueError):
        parse_request(request_bytes)


@pytest.mark.parametrize(
    "http_method, path, expected_status",
    [
        ("GET", "/", 200),
        ("GET", "/echo/hi?x=1", 200),
        ("GET", "/missing", 404),
        ("GET", "/echo", 404),
        ("POST", "/", 405),
    ],
)
def test_choose_response_status_code(http_method, path, expected_status):
    status_code, _response_text = choose_response(http_method, path, {})
    assert status_code == expected_status


def test_build_http_response_has_status_line_length_and_body():
    response_bytes = build_http_response(404, "no")
    assert response_bytes.startswith(b"HTTP/1.1 404 Not Found\r\n")
    assert b"Content-Length: 2\r\n" in response_bytes
    assert response_bytes.endswith(b"\r\n\r\nno")


def test_root_echo_and_user_agent_over_a_real_socket(server):
    assert get_response(server) == (200, b"tiny-http-toolkit is running")
    assert get_response(server, path="/echo/hello%20world") == (200, b"hello world")
    user_agent_headers = {"User-Agent": "test-agent"}
    assert get_response(server, path="/user-agent", headers=user_agent_headers) == (
        200,
        b"test-agent",
    )


def test_unknown_path_gets_404_and_post_gets_405(server):
    assert get_response(server, path="/nope")[0] == 404
    assert get_response(server, "POST", "/")[0] == 405


def test_malformed_request_gets_400(server):
    assert send_raw_bytes(server, b"NONSENSE\r\n\r\n").startswith(b"HTTP/1.1 400")


def test_silent_client_does_not_block_the_server_forever(server):
    with socket.create_connection(("127.0.0.1", server)):
        assert get_response(server)[0] == 200
