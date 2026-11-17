"""Request log stored in a file (JSON Lines: one JSON object per line).

Results are written here instead of being printed, and shown later by ``display_log``.
"""

import json
from pathlib import Path


def send_to_log(log_path: str, log_entry: dict) -> None:
    """Append ``log_entry`` as one line to the log file, creating the file if needed.

    Raises:
        OSError: if the file cannot be created or written.
        TypeError: if ``log_entry`` is not JSON serialisable.
    """
    serialized_entry = json.dumps(log_entry, ensure_ascii=False)
    log_file_path = Path(log_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    with log_file_path.open("a", encoding="utf-8") as log_file:
        log_file.write(serialized_entry + "\n")


def read_log(log_path: str) -> list[dict]:
    """Return all valid entries of the log file; unreadable lines are skipped.

    A missing file gives an empty list.

    Raises:
        OSError: if the file exists but cannot be read.
    """
    log_entries = []
    try:
        with open(log_path, encoding="utf-8", errors="replace") as log_file:
            for line in log_file:
                try:
                    parsed_line = json.loads(line)
                except ValueError:
                    continue
                if isinstance(parsed_line, dict):
                    log_entries.append(parsed_line)
    except FileNotFoundError:
        return []
    return log_entries


def display_log(log_path: str) -> None:
    """Print every entry of the log file, oldest first.

    Raises:
        OSError: if the file exists but cannot be read.
    """
    log_entries = read_log(log_path)
    if not log_entries:
        print("The log is empty.")
    for entry_number, log_entry in enumerate(log_entries, start=1):
        outcome = log_entry.get("error") or (
            f"{log_entry.get('status')} {log_entry.get('body')}"
        )
        print(
            f"#{entry_number} {log_entry.get('timestamp')} {log_entry.get('url')}\n"
            f"    {outcome}"
        )
