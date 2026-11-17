import pytest

from httpkit.storage import display_log, read_log, send_to_log


def test_entries_sent_to_the_log_are_read_back_in_order(tmp_path):
    log_path = str(tmp_path / "nested" / "log.jsonl")
    send_to_log(log_path, {"number": 1})
    send_to_log(log_path, {"number": 2, "text": "привіт ✓"})
    assert read_log(log_path) == [{"number": 1}, {"number": 2, "text": "привіт ✓"}]


def test_reading_a_missing_log_gives_an_empty_list(tmp_path):
    assert read_log(str(tmp_path / "missing.jsonl")) == []


def test_reading_skips_corrupt_blank_and_non_object_lines(tmp_path):
    log_file = tmp_path / "log.jsonl"
    log_file.write_text('{"a": 1}\nnot json\n\n[1, 2]\n{"b": 2}\n', encoding="utf-8")
    assert read_log(str(log_file)) == [{"a": 1}, {"b": 2}]


def test_sending_fails_when_the_log_directory_cannot_be_created(tmp_path):
    file_in_the_way = tmp_path / "file"
    file_in_the_way.write_text("x")
    with pytest.raises(FileExistsError):
        send_to_log(str(file_in_the_way / "log.jsonl"), {"a": 1})


def test_sending_rejects_entries_that_are_not_json_serialisable(tmp_path):
    with pytest.raises(TypeError):
        send_to_log(str(tmp_path / "log.jsonl"), {"unserialisable": {1, 2}})


def test_failed_serialisation_does_not_create_the_log_file(tmp_path):
    log_path = tmp_path / "log.jsonl"
    with pytest.raises(TypeError):
        send_to_log(str(log_path), {"unserialisable": {1, 2}})
    assert not log_path.exists()


def test_reading_survives_bytes_that_are_not_valid_utf8(tmp_path):
    log_file = tmp_path / "log.jsonl"
    log_file.write_bytes(b'{"a": 1}\n\xff\xfe broken\n{"b": 2}\n')
    assert read_log(str(log_file)) == [{"a": 1}, {"b": 2}]


def test_display_prints_results_and_errors(tmp_path, capsys):
    log_path = str(tmp_path / "log.jsonl")
    send_to_log(
        log_path,
        {"timestamp": "T1", "url": "http://h/a", "status": 200, "body": "hi"},
    )
    send_to_log(log_path, {"timestamp": "T2", "url": "http://h/b", "error": "refused"})
    display_log(log_path)
    printed = capsys.readouterr().out
    assert "#1 T1 http://h/a\n    200 hi" in printed
    assert "#2 T2 http://h/b\n    refused" in printed


def test_display_of_a_missing_log_says_it_is_empty(tmp_path, capsys):
    display_log(str(tmp_path / "missing.jsonl"))
    assert capsys.readouterr().out.strip() == "The log is empty."
