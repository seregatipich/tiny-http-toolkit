import pytest

from httpkit.storage import display_log, read_log, send_to_log


def test_send_then_read_round_trips_in_order(tmp_path):
    log = str(tmp_path / "nested" / "log.jsonl")
    send_to_log(log, {"n": 1})
    send_to_log(log, {"n": 2, "text": "привіт ✓"})
    assert read_log(log) == [{"n": 1}, {"n": 2, "text": "привіт ✓"}]


def test_read_log_missing_file_is_empty(tmp_path):
    assert read_log(str(tmp_path / "nope.jsonl")) == []


def test_read_log_skips_corrupt_blank_and_non_object_lines(tmp_path):
    log = tmp_path / "log.jsonl"
    log.write_text('{"a": 1}\nnot json\n\n[1, 2]\n{"b": 2}\n', encoding="utf-8")
    assert read_log(str(log)) == [{"a": 1}, {"b": 2}]


def test_send_to_log_propagates_os_errors(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(OSError):
        send_to_log(str(blocker / "log.jsonl"), {"a": 1})


def test_send_to_log_rejects_unserialisable_entry(tmp_path):
    with pytest.raises(TypeError):
        send_to_log(str(tmp_path / "log.jsonl"), {"bad": {1, 2}})


def test_display_log_prints_results_and_errors(tmp_path, capsys):
    log = str(tmp_path / "log.jsonl")
    send_to_log(
        log, {"timestamp": "T1", "url": "http://h/a", "status": 200, "body": "hi"}
    )
    send_to_log(log, {"timestamp": "T2", "url": "http://h/b", "error": "refused"})
    display_log(log)
    out = capsys.readouterr().out
    assert "#1 T1 http://h/a\n    200 hi" in out
    assert "#2 T2 http://h/b\n    refused" in out


def test_display_log_empty(tmp_path, capsys):
    display_log(str(tmp_path / "missing.jsonl"))
    assert capsys.readouterr().out.strip() == "The log is empty."
