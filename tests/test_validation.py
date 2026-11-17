import pytest

from httpkit.validation import validate_port, validate_url


@pytest.mark.parametrize(
    ("user_input", "expected_port"), [("8080", 8080), (" 0 ", 0), ("65535", 65535)]
)
def test_validate_port_accepts_numbers_in_range(user_input, expected_port):
    assert validate_port(user_input) == expected_port


@pytest.mark.parametrize(
    "user_input", ["abc", "", "-1", "+80", "65536", "80.5", "8_080", "８０８０"]
)
def test_validate_port_rejects_everything_else(user_input):
    with pytest.raises(ValueError, match="Port must"):
        validate_port(user_input)


@pytest.mark.parametrize("user_input", ["http://h:1/a", " https://example.com "])
def test_validate_url_accepts_http_and_https(user_input):
    assert validate_url(user_input) == user_input.strip()


@pytest.mark.parametrize(
    "user_input",
    [
        "",
        "example.com",
        "ftp://host",
        "http://",
        "http://:80",
        "http://host:abc",
        "/echo/hi",
    ],
)
def test_validate_url_rejects_missing_scheme_unsupported_scheme_or_host(user_input):
    with pytest.raises(ValueError, match="URL must|URL has"):
        validate_url(user_input)
