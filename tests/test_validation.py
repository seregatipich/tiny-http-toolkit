import pytest

from httpkit.validation import validate_port, validate_url


@pytest.mark.parametrize(
    "raw, expected", [("8080", 8080), (" 0 ", 0), ("65535", 65535)]
)
def test_validate_port_accepts(raw, expected):
    assert validate_port(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "", "-1", "65536", "80.5"])
def test_validate_port_rejects(raw):
    with pytest.raises(ValueError):
        validate_port(raw)


@pytest.mark.parametrize("raw", ["http://h:1/a", " https://example.com "])
def test_validate_url_accepts(raw):
    assert validate_url(raw) == raw.strip()


@pytest.mark.parametrize(
    "raw", ["", "example.com", "ftp://host", "http://", "/echo/hi"]
)
def test_validate_url_rejects(raw):
    with pytest.raises(ValueError):
        validate_url(raw)
