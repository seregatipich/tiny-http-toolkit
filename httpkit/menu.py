"""Interactive console menu that ties the server, client and log together."""

from httpkit.client import call_api
from httpkit.server import start_server
from httpkit.storage import display_log, send_to_log
from httpkit.validation import validate_port, validate_url


def ask(prompt: str, validator, default: str = ""):
    """Prompt until ``validator`` accepts the answer; an empty answer uses ``default``."""
    suffix = f" [{default}]" if default else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip() or default
        try:
            return validator(raw)
        except ValueError as exc:
            print(f"Invalid input: {exc}")


def start_action(state: dict) -> None:
    """Menu action: start the built-in server on a port chosen by the user."""
    if state["server"]:
        print("Server is already running.")
        return
    port = ask("Port", validate_port, "8080")
    try:
        state["server"] = start_server(state["host"], port)
    except OSError as exc:
        print(f"Could not start the server: {exc.strerror or exc}")
        return
    print(
        f"Server listening on http://{state['host']}:{state['server'].getsockname()[1]}"
    )


def send_action(state: dict) -> None:
    """Menu action: GET a URL and save the result to the log without printing it."""
    server = state["server"]
    port = server.getsockname()[1] if server else 8080
    url = ask("URL", validate_url, f"http://{state['host']}:{port}/echo/hello")
    try:
        send_to_log(state["log_path"], call_api(url))
    except OSError as exc:
        print(f"Could not save the result: {exc.strerror or exc}")
        return
    print("Result saved to the log. Choose 'View log' to read it.")


def view_action(state: dict) -> None:
    """Menu action: show everything stored in the log file."""
    try:
        display_log(state["log_path"])
    except OSError as exc:
        print(f"Could not read the log: {exc.strerror or exc}")


def run_menu(log_path: str = "data/history.jsonl") -> None:
    """Show the menu and run the chosen actions until the user quits."""
    state: dict = {"host": "127.0.0.1", "log_path": log_path, "server": None}
    options = (
        ("1", "Start server", start_action),
        ("2", "Send request (result goes to the log)", send_action),
        ("3", "View log", view_action),
    )
    actions = {key: action for key, _, action in options}
    try:
        while True:
            print("\n=== Tiny HTTP Toolkit ===")
            for key, label, _ in options:
                print(f"{key}) {label}")
            choice = input("0) Quit\nChoose: ").strip()
            if choice == "0":
                break
            if choice in actions:
                actions[choice](state)
            else:
                print(f"Unknown option {choice!r}.")
    except (EOFError, KeyboardInterrupt):
        print()
    if state["server"]:
        state["server"].close()
