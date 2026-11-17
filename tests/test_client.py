import socket

from httpkit.client import call_api


def test_call_api_records_status_and_body(server):
    entry = call_api(f"http://127.0.0.1:{server}/echo/hello")
    assert entry["url"] == f"http://127.0.0.1:{server}/echo/hello"
    assert (entry["status"], entry["body"]) == (200, "hello")
    assert "T" in entry["timestamp"]
    assert "error" not in entry


def test_call_api_cuts_long_bodies(server):
    entry = call_api(f"http://127.0.0.1:{server}/echo/{'x' * 600}")
    assert len(entry["body"]) == 500


def test_call_api_records_http_errors_as_results(server):
    entry = call_api(f"http://127.0.0.1:{server}/missing")
    assert entry["status"] == 404
    assert "error" not in entry


def test_call_api_records_connection_refused():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    entry = call_api(f"http://127.0.0.1:{port}/")
    assert "ConnectionError" in entry["error"]
    assert "status" not in entry


def test_call_api_records_timeout():
    with socket.socket() as silent:
        silent.bind(("127.0.0.1", 0))
        silent.listen(1)
        entry = call_api(f"http://127.0.0.1:{silent.getsockname()[1]}/", timeout=0.3)
    assert "Timeout" in entry["error"]
