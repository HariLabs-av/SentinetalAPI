import pytest

from sentinelapi.security import TargetError, safe_url, validate_target


def test_localhost_is_allowed_for_sandbox():
    assert validate_target("http://localhost:8080") == "http://localhost:8080"


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com", "http://user:pass@example.com"])
def test_unsafe_target_is_rejected(url):
    with pytest.raises(TargetError):
        validate_target(url)


def test_cross_origin_path_is_rejected():
    with pytest.raises(TargetError):
        safe_url("http://localhost:8000", "//evil.example/x")
