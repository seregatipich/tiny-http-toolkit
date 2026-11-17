# tiny-http-toolkit

A small console app built around a minimal HTTP server (a stripped-down version of [http-server-python](https://github.com/seregatipich/http-server-python)).

From a menu you start the built-in server, call its API (or any other HTTP API) with `requests`, and read the results later from a log file. Results are **not printed when a request is sent**: they are appended to `data/history.jsonl` and shown on demand with "View log", so nothing has to be requested again.

## Setup

Requires Python 3.10+.

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

Data structures: dicts (log entries, headers, state), lists (log entries), sets (allowed URL schemes), tuples (request line, route result, menu options).

## Tests

```bash
python -m pytest
```
