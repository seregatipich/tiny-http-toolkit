import pytest

from httpkit.menu import run_menu
from httpkit.storage import read_log


@pytest.fixture
def log_path(tmp_path):
    return str(tmp_path / "log.jsonl")


@pytest.fixture
def feed(monkeypatch):
    def install(*answers):
        queue = iter(answers)

        def fake_input(prompt=""):
            try:
                return next(queue)
            except StopIteration:
                raise EOFError from None

        monkeypatch.setattr("builtins.input", fake_input)

    return install


def test_send_saves_to_file_without_printing_the_result(log_path, feed, capsys):
    feed("1", "0", "2", "", "0")
    run_menu(log_path)
    out = capsys.readouterr().out
    assert "Result saved to the log" in out
    assert "hello" not in out
    assert read_log(log_path)[0]["body"] == "hello"


def test_view_log_shows_saved_result_later(log_path, feed, capsys):
    feed("1", "0", "2", "", "3", "0")
    run_menu(log_path)
    out = capsys.readouterr().out
    assert "#1" in out and "200 hello" in out


def test_log_persists_between_sessions(log_path, feed, capsys):
    feed("1", "0", "2", "", "0")
    run_menu(log_path)
    feed("3", "0")
    run_menu(log_path)
    assert "200 hello" in capsys.readouterr().out


def test_invalid_answers_are_asked_again(log_path, feed, capsys):
    feed("1", "99999", "abc", "0", "2", "echo", "ftp://x", "", "0")
    run_menu(log_path)
    out = capsys.readouterr().out
    assert out.count("Invalid input") == 4
    assert len(read_log(log_path)) == 1


def test_unknown_choice(log_path, feed, capsys):
    feed("9", "0")
    run_menu(log_path)
    assert "Unknown option '9'" in capsys.readouterr().out


def test_second_start_is_refused(log_path, feed, capsys):
    feed("1", "0", "1", "0")
    run_menu(log_path)
    assert "already running" in capsys.readouterr().out


def test_start_on_busy_port_reports_error(log_path, feed, capsys, server_port):
    feed("1", str(server_port), "0")
    run_menu(log_path)
    assert "Could not start the server" in capsys.readouterr().out


def test_unreachable_url_is_logged_not_crashed(log_path, feed, capsys):
    feed("2", "http://127.0.0.1:9/", "3", "0")
    run_menu(log_path)
    assert "ConnectionError" in capsys.readouterr().out


def test_unwritable_log_is_reported(tmp_path, feed, capsys):
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    feed("1", "0", "2", "", "0")
    run_menu(str(blocker / "log.jsonl"))
    assert "Could not save the result" in capsys.readouterr().out


def test_unreadable_log_is_reported(tmp_path, feed, capsys):
    feed("3", "0")
    run_menu(str(tmp_path))
    assert "Could not read the log" in capsys.readouterr().out


def test_eof_exits_cleanly(log_path, feed):
    feed("1", "0")
    run_menu(log_path)
