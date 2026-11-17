"""Interactive console menu that ties the server, client and log together."""

from collections.abc import Callable
from typing import Any

from httpkit.client import call_api
from httpkit.server import start_server
from httpkit.storage import display_log, send_to_log
from httpkit.validation import validate_port, validate_url


def prompt_until_valid(
    prompt: str, validate: Callable[[str], Any], default_answer: str = ""
) -> Any:
    """Ask the user until ``validate`` accepts the answer, then return its result.

    An empty answer means ``default_answer``. Validation errors are printed and the
    question is asked again.
    """
    default_hint = f" [{default_answer}]" if default_answer else ""
    while True:
        answer = input(f"{prompt}{default_hint}: ").strip() or default_answer
        try:
            return validate(answer)
        except ValueError as validation_error:
            print(f"Invalid input: {validation_error}")


def start_server_action(app_state: dict) -> None:
    """Menu action: start the built-in server on a port chosen by the user."""
    if app_state["server_socket"]:
        print("Server is already running.")
        return
    port = prompt_until_valid(
        "Port", validate_port, default_answer=str(app_state["default_port"])
    )
    try:
        app_state["server_socket"] = start_server(app_state["host"], port)
    except OSError as start_error:
        print(f"Could not start the server: {start_error.strerror or start_error}")
        return
    actual_port = app_state["server_socket"].getsockname()[1]
    print(f"Server listening on http://{app_state['host']}:{actual_port}")


def send_request_action(app_state: dict) -> None:
    """Menu action: GET a URL and save the result to the log without printing it."""
    server_socket = app_state["server_socket"]
    if server_socket:
        server_port = server_socket.getsockname()[1]
    else:
        server_port = app_state["default_port"]
    default_url = f"http://{app_state['host']}:{server_port}/echo/hello"
    url = prompt_until_valid("URL", validate_url, default_answer=default_url)
    try:
        send_to_log(app_state["log_path"], call_api(url))
    except OSError as save_error:
        print(f"Could not save the result: {save_error.strerror or save_error}")
        return
    print("Result saved to the log. Choose 'View log' to read it.")


def view_log_action(app_state: dict) -> None:
    """Menu action: show everything stored in the log file."""
    try:
        display_log(app_state["log_path"])
    except OSError as read_error:
        print(f"Could not read the log: {read_error.strerror or read_error}")


def run_menu(log_path: str = "data/history.jsonl") -> None:
    """Show the menu and run the chosen actions until the user quits.

    The actions share ``app_state``, a dict with the keys ``host`` and
    ``default_port`` (where the built-in server listens), ``log_path`` (the log file)
    and ``server_socket`` (the running server's socket, or None).
    """
    app_state: dict = {
        "host": "127.0.0.1",
        "default_port": 8080,
        "log_path": log_path,
        "server_socket": None,
    }
    quit_key = "0"
    menu_options = (
        ("1", "Start server", start_server_action),
        ("2", "Send request (result goes to the log)", send_request_action),
        ("3", "View log", view_log_action),
    )
    action_by_key = {key: action for key, _label, action in menu_options}
    try:
        while True:
            print("\n=== Tiny HTTP Toolkit ===")
            for key, label, _action in menu_options:
                print(f"{key}) {label}")
            menu_choice = input(f"{quit_key}) Quit\nChoose: ").strip()
            if menu_choice == quit_key:
                break
            if menu_choice in action_by_key:
                action_by_key[menu_choice](app_state)
            else:
                print(f"Unknown option {menu_choice!r}.")
    except (EOFError, KeyboardInterrupt):
        print()
    if app_state["server_socket"]:
        app_state["server_socket"].close()
