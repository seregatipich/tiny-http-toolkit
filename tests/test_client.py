import socket

from httpkit.client import call_api


def test_call_api_records_status_and_body(server_port):
    url = f"http://127.0.0.1:{server_port}/echo/hello"
    log_entry = call_api(url)
    assert log_entry["url"] == url
    assert (log_entry["status"], log_entry["body"]) == (200, "hello")
    assert "T" in log_entry["timestamp"]
    assert "error" not in log_entry


def test_call_api_cuts_long_bodies_to_the_limit(server_port):
    log_entry = call_api(f"http://127.0.0.1:{server_port}/echo/{'x' * 600}")
    assert len(log_entry["body"]) == 500
    log_entry = call_api(
        f"http://127.0.0.1:{server_port}/echo/{'x' * 600}", max_body_chars=10
    )
    assert log_entry["body"] == "x" * 10


def test_call_api_records_http_error_statuses_as_results(server_port):
    log_entry = call_api(f"http://127.0.0.1:{server_port}/missing")
    assert log_entry["status"] == 404
    assert "error" not in log_entry


def test_call_api_records_connection_refused_as_error():
    with socket.socket() as reserved_socket:
        reserved_socket.bind(("127.0.0.1", 0))
        closed_port = reserved_socket.getsockname()[1]
    log_entry = call_api(f"http://127.0.0.1:{closed_port}/")
    assert "ConnectionError" in log_entry["error"]
    assert "status" not in log_entry


def test_call_api_records_timeout_as_error():
    with socket.socket() as silent_server_socket:
        silent_server_socket.bind(("127.0.0.1", 0))
        silent_server_socket.listen(1)
        silent_port = silent_server_socket.getsockname()[1]
        log_entry = call_api(f"http://127.0.0.1:{silent_port}/", timeout_seconds=0.3)
    assert "Timeout" in log_entry["error"]
