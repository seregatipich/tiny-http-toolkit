"""Validation of what the user types. Every validator raises ``ValueError``."""

from urllib.parse import urlsplit


def validate_port(user_input: str) -> int:
    """Convert ``user_input`` to a TCP port number (0 means "pick a free port").

    Raises:
        ValueError: if ``user_input`` is not a whole number between 0 and 65535.
    """
    try:
        port_number = int(user_input.strip())
    except ValueError:
        raise ValueError(f"Port must be a whole number, got {user_input!r}.") from None
    if not 0 <= port_number <= 65535:
        raise ValueError("Port must be between 0 and 65535.")
    return port_number


def validate_url(user_input: str) -> str:
    """Return ``user_input`` without surrounding spaces, if it is an http(s) URL.

    Raises:
        ValueError: if the scheme is missing or is not http/https, or if there is no host.
    """
    url = user_input.strip()
    url_parts = urlsplit(url)
    if url_parts.scheme not in {"http", "https"}:
        raise ValueError("URL must start with http:// or https://.")
    host_and_port = url_parts.netloc
    if not host_and_port:
        raise ValueError("URL must include a host.")
    return url
