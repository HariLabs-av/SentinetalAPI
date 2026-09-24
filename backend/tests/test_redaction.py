from sentinelapi.redaction import redact


def test_secret_fields_are_redacted():
    value = redact({"password": "secret", "nested": {"access_token": "long-token-value"}})
    assert value == {"password": "<REDACTED>", "nested": {"access_token": "<REDACTED>"}}
