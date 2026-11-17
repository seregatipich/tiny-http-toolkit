"""Validation of what the user types. Every validator raises ``ValueError``."""

from urllib.parse import urlsplit


def validate_port(user_input: str) -> int:
    """Convert ``user_input`` to a TCP port number (0 means "pick a free port").

    Raises:
        ValueError: if ``user_input`` is not made of ASCII digits or is above 65535.
    """
    digits = user_input.strip()
    if not (digits.isascii() and digits.isdigit()):
        raise ValueError(f"Port must be a whole number, got {user_input!r}.")
    port_number = int(digits)
    if port_number > 65535:
        raise ValueError("Port must be at most 65535.")
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
    if not url_parts.hostname:
        raise ValueError("URL must include a host.")
    try:
        _explicit_port = url_parts.port
    except ValueError:
        raise ValueError("URL has an invalid port.") from None
    return url
