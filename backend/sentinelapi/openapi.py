from typing import Any
import json
import logging

import httpx
import yaml

from .config import settings
from .security import safe_url, validate_target

log = logging.getLogger(__name__)
COMMON_PATHS = ("/openapi.json", "/openapi.yaml", "/swagger.json", "/v3/api-docs")


def _parse_document(content: bytes, content_type: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(content) if ("yaml" in content_type.lower() or not content_type) else json.loads(content)
    except (ValueError, yaml.YAMLError) as exc:
        raise ValueError("OpenAPI document is malformed") from exc
    if not isinstance(data, dict) or not (data.get("openapi") or data.get("swagger")):
        raise ValueError("response is not an OpenAPI/Swagger document")
    return data


def discover(target: str, explicit: str | None = None) -> dict[str, Any]:
    base = validate_target(target)
    candidates = [validate_target(explicit)] if explicit else [safe_url(base, path) for path in COMMON_PATHS]
    with httpx.Client(timeout=settings.request_timeout, follow_redirects=False, max_redirects=0) as client:
        for candidate in candidates:
            try:
                response = client.get(candidate)
                if response.status_code == 200 and len(response.content) <= settings.max_response_bytes:
                    document = _parse_document(response.content, response.headers.get("content-type", ""))
                    return parse_document(document, candidate)
            except (httpx.HTTPError, ValueError) as exc:
                log.debug("OpenAPI candidate failed: %s", type(exc).__name__)
    return {"found": False, "url": None, "version": None, "endpoints": [], "security_schemes": {}}


def parse_document(document: dict[str, Any], source_url: str) -> dict[str, Any]:
    endpoints = []
    for path, path_item in (document.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options"} or not isinstance(operation, dict):
                continue
            parameters = (path_item.get("parameters", []) if isinstance(path_item.get("parameters"), list) else []) + operation.get("parameters", [])
            endpoints.append({
                "path": path, "method": method.upper(), "operation_id": operation.get("operationId"),
                "parameters": [{"name": p.get("name"), "in": p.get("in"), "required": p.get("required", False)} for p in parameters if isinstance(p, dict)],
                "responses": sorted(str(k) for k in (operation.get("responses") or {})),
            })
    return {
        "found": True, "url": source_url, "version": document.get("openapi") or document.get("swagger"),
        "title": (document.get("info") or {}).get("title"), "endpoints": endpoints,
        "security_schemes": ((document.get("components") or {}).get("securitySchemes") or document.get("securityDefinitions") or {}),
    }
