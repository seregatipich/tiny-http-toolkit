"""API client: one GET request, described as a dict ready for the log."""

from datetime import datetime

import requests


def call_api(url: str, timeout: float = 5.0) -> dict:
    """Send a GET request to ``url`` and describe the result.

    Network problems do not raise; they are stored under ``error`` so they can be
    reviewed in the log like any other result.

    Returns:
        ``{"timestamp", "url", "status", "body"}`` (body cut to 500 characters) or
        ``{"timestamp", "url", "error"}``.
    """
    entry: dict = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "url": url,
    }
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        entry["error"] = f"{type(exc).__name__}: {exc}"
    else:
        entry["status"] = response.status_code
        entry["body"] = response.text[:500]
    return entry
