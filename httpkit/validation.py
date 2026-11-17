"""Validation of what the user types. Every validator raises ``ValueError``."""

from urllib.parse import urlsplit


def validate_port(raw: str) -> int:
    """Convert ``raw`` to a TCP port number (0 means "pick a free port").

    Raises:
        ValueError: if ``raw`` is not a whole number between 0 and 65535.
    """
    try:
        port = int(raw.strip())
    except ValueError:
        raise ValueError(f"Port must be a whole number, got {raw!r}.") from None
    if not 0 <= port <= 65535:
        raise ValueError("Port must be between 0 and 65535.")
    return port


def validate_url(raw: str) -> str:
    """Return ``raw`` stripped, if it is an http(s) URL with a host.

    Raises:
        ValueError: for a missing or unsupported scheme or a missing host.
    """
    url = raw.strip()
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        raise ValueError("URL must start with http:// or https://.")
    if not parts.netloc:
        raise ValueError("URL must include a host.")
    return url
