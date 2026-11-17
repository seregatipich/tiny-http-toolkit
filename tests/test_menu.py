import pytest

from httpkit.menu import run_menu
from httpkit.storage import read_log


def start_on_free_port():
    """Answers that choose "Start server" and then port 0 (any free port)."""
    return ["1", "0"]


def send_request_to(url=""):
    """Answers that choose "Send request"; an empty url accepts the default one."""
    return ["2", url]


def view_log():
    """Answers that choose "View log"."""
    return ["3"]


def quit_menu():
    """Answers that choose "Quit"."""
    return ["0"]


@pytest.fixture
def log_path(tmp_path):
    return str(tmp_path / "log.jsonl")


@pytest.fixture
def type_answers(monkeypatch):
    """Return a function that makes ``input()`` return the given answers in order.

    When the answers run out, ``input()`` raises EOFError like a closed terminal.
    """

    def install(*answers):
        remaining_answers = iter(answers)

        def fake_input(prompt=""):
            try:
                return next(remaining_answers)
            except StopIteration:
                raise EOFError from None

        monkeypatch.setattr("builtins.input", fake_input)

    return install


def test_sending_saves_to_the_file_without_printing_the_result(
    log_path, type_answers, capsys
):
    type_answers(*start_on_free_port(), *send_request_to(), *quit_menu())
    run_menu(log_path)
    printed_output = capsys.readouterr().out
    assert "Result saved to the log" in printed_output
    assert "hello" not in printed_output
    assert read_log(log_path)[0]["body"] == "hello"


def test_viewing_the_log_shows_the_saved_result_later(log_path, type_answers, capsys):
    type_answers(*start_on_free_port(), *send_request_to(), *view_log(), *quit_menu())
    run_menu(log_path)
    printed_output = capsys.readouterr().out
    assert "#1" in printed_output
    assert "200 hello" in printed_output


def test_log_survives_restarting_the_app(log_path, type_answers, capsys):
    type_answers(*start_on_free_port(), *send_request_to(), *quit_menu())
    run_menu(log_path)
    type_answers(*view_log(), *quit_menu())
    run_menu(log_path)
    assert "200 hello" in capsys.readouterr().out


def test_invalid_answers_are_asked_again(log_path, type_answers, capsys):
    invalid_ports_then_free_port = ["1", "99999", "abc", "0"]
    invalid_urls_then_default_url = ["2", "echo", "ftp://x", ""]
    type_answers(
        *invalid_ports_then_free_port, *invalid_urls_then_default_url, *quit_menu()
    )
    run_menu(log_path)
    assert capsys.readouterr().out.count("Invalid input") == 4
    assert len(read_log(log_path)) == 1


def test_unknown_menu_choice_is_reported(log_path, type_answers, capsys):
    type_answers("9", *quit_menu())
    run_menu(log_path)
    assert "Unknown option '9'" in capsys.readouterr().out


def test_starting_the_server_twice_is_refused(log_path, type_answers, capsys):
    type_answers(*start_on_free_port(), *start_on_free_port(), *quit_menu())
    run_menu(log_path)
    assert "already running" in capsys.readouterr().out


def test_starting_on_a_busy_port_is_reported(
    log_path, type_answers, capsys, server_port
):
    type_answers("1", str(server_port), *quit_menu())
    run_menu(log_path)
    assert "Could not start the server" in capsys.readouterr().out


def test_unreachable_url_is_logged_as_an_error_not_a_crash(
    log_path, type_answers, capsys
):
    type_answers(*send_request_to("http://127.0.0.1:9/"), *view_log(), *quit_menu())
    run_menu(log_path)
    assert "ConnectionError" in capsys.readouterr().out


def test_unwritable_log_is_reported(tmp_path, type_answers, capsys):
    file_in_the_way = tmp_path / "file_in_the_way"
    file_in_the_way.write_text("x")
    type_answers(*start_on_free_port(), *send_request_to(), *quit_menu())
    run_menu(str(file_in_the_way / "log.jsonl"))
    assert "Could not save the result" in capsys.readouterr().out


def test_unreadable_log_is_reported(tmp_path, type_answers, capsys):
    directory_instead_of_file = str(tmp_path)
    type_answers(*view_log(), *quit_menu())
    run_menu(directory_instead_of_file)
    assert "Could not read the log" in capsys.readouterr().out


def test_closing_the_terminal_exits_cleanly(log_path, type_answers):
    type_answers(*start_on_free_port())
    run_menu(log_path)
