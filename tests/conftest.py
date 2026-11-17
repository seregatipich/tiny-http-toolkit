import pytest

from httpkit.server import start_server


@pytest.fixture
def server():
    """Port of a real server running on a free local port."""
    sock = start_server("127.0.0.1", 0)
    yield sock.getsockname()[1]
    sock.close()
