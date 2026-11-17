"""Request log stored in a file (JSON Lines: one JSON object per line).

Results are written here instead of being printed, and shown later by ``display_log``.
"""

import json
from pathlib import Path


def send_to_log(path: str, entry: dict) -> None:
    """Append ``entry`` as one line to the log at ``path``, creating it if needed.

    Raises:
        OSError: if the file cannot be created or written.
        TypeError: if ``entry`` is not JSON serialisable.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_log(path: str) -> list[dict]:
    """Return all valid entries of the log at ``path``; unreadable lines are skipped.

    A missing file gives an empty list.

    Raises:
        OSError: if the file exists but cannot be read.
    """
    if not Path(path).exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def display_log(path: str) -> None:
    """Print every entry of the log at ``path``, oldest first.

    Raises:
        OSError: if the file exists but cannot be read.
    """
    entries = read_log(path)
    if not entries:
        print("The log is empty.")
    for number, entry in enumerate(entries, start=1):
        result = entry.get("error") or f"{entry.get('status')} {entry.get('body')}"
        print(f"#{number} {entry.get('timestamp')} {entry.get('url')}\n    {result}")
