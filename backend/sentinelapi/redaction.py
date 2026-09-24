import re
from typing import Any


SECRET_KEYS = re.compile(r"(password|passwd|token|secret|api[_-]?key|authorization|cookie|session)", re.I)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): "<REDACTED>" if SECRET_KEYS.search(str(k)) else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str) and len(value) > 20:
        return value[:4] + "<REDACTED>"
    return value


def safe_headers(token: str | None = None) -> dict[str, str]:
    return {"Authorization": "Bearer <REDACTED>"} if token else {}
