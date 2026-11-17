import pytest

from httpkit.server import start_server


@pytest.fixture
def server_port():
    """Port of a real server running on a free local port."""
    listening_socket = start_server("127.0.0.1", 0)
    yield listening_socket.getsockname()[1]
    listening_socket.close()
