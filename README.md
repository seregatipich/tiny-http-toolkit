# tiny-http-toolkit

A small console app built around a minimal HTTP server.

From a menu you start the built-in server, call its API (or any other HTTP API) with `requests`, and read the results later from a log file. Results are **not printed when a request is sent**: they are appended to `data/history.jsonl` and shown on demand with "View log", so nothing has to be requested again.

## Setup

Requires Python 3.10 or newer (tested on 3.10, 3.12 and 3.14).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

```
1) Start server
2) Send request (result goes to the log)
3) View log
0) Quit
```

Typical session: `1` start the server, `2` send `GET /echo/hello`, `3` view the log, `0` quit.

## Server endpoints

GET only, plain text, bound to `127.0.0.1`. It answers one client at a time and drops clients that stay silent for a second.

| Path | Result |
| --- | --- |
| `/` | status text |
| `/echo/<message>` | the URL-decoded message |
| `/user-agent` | the caller's `User-Agent` |

## Layout

| File | Purpose |
| --- | --- |
| `main.py` | entry point |
| `httpkit/menu.py` | menu and user interaction |
| `httpkit/validation.py` | validation of typed input |
| `httpkit/client.py` | API client (`requests`) |
| `httpkit/server.py` | socket HTTP server |
| `httpkit/storage.py` | log file: `send_to_log`, `read_log`, `display_log` |

Data structures: dicts (log entries, request headers, app state), lists (log entries read from the file), sets (allowed URL schemes), tuples (parsed request, status code and response text, menu options).

## Tests and checks

```bash
python -m pytest
ruff format --check .
ruff check .
mypy
```

The tests start a real server on a free port.
