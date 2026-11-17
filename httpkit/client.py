"""API client: one GET request, described as a dict ready for the log."""

from datetime import datetime

import requests


def call_api(url: str, timeout_seconds: float = 5.0, max_body_chars: int = 500) -> dict:
    """Send a GET request to ``url`` and describe the result as a log entry.

    Network problems do not raise; they are stored under ``error`` so they can be
    reviewed in the log like any other result.

    Returns:
        ``{"timestamp", "url", "status", "body"}`` (body cut to ``max_body_chars``
        characters) or ``{"timestamp", "url", "error"}``.
    """
    log_entry: dict = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "url": url,
    }
    try:
        response = requests.get(url, timeout=timeout_seconds)
    except requests.exceptions.RequestException as request_error:
        log_entry["error"] = f"{type(request_error).__name__}: {request_error}"
    else:
        log_entry["status"] = response.status_code
        log_entry["body"] = response.text[:max_body_chars]
    return log_entry
