from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import re
import time
from typing import Any
from uuid import uuid4

import httpx

from .config import settings
from .models import Finding, Poc
from .redaction import redact, safe_headers
from .security import safe_url

log = logging.getLogger(__name__)
SENSITIVE = re.compile(r"(password|password_hash|secret|token|api[_-]?key|ssn|credit[_-]?card|internal[_-]?role|internal[_-]?id)", re.I)
MODES = {"easy": {"requests": 3, "workers": 1}, "moderate": {"requests": 8, "workers": 3}, "brutal": {"requests": 16, "workers": 6}}


def _json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def authenticate(client: httpx.Client, base: str, path: str, identity: dict[str, str]) -> str | None:
    response = client.post(safe_url(base, path), json=identity)
    if response.status_code >= 400:
        return None
    body = _json(response)
    if isinstance(body, dict):
        for key in ("token", "access_token", "accessToken", "jwt"):
            if isinstance(body.get(key), str):
                return body[key]
    return None


def _resource_path(endpoint: dict[str, Any]) -> str | None:
    path = endpoint["path"]
    match = re.search(r"\{([^}]+)\}", path)
    return path.replace(match.group(0), "1") if match else None


def scan(session_id: str, target: str, discovery: dict[str, Any], mode: str, login_path: str, identity_a: dict[str, str], identity_b: dict[str, str]) -> dict[str, Any]:
    started = time.monotonic()
    config = MODES[mode]
    findings: list[Finding] = []
    pocs: list[Poc] = []
    requests_made = 0
    status_counts: dict[str, int] = {}
    rate_limit_observations = {"responses_2xx": 0, "responses_4xx": 0, "responses_429": 0, "responses_5xx": 0, "timeouts": 0}

    def record(response: httpx.Response) -> None:
        nonlocal requests_made
        requests_made += 1
        status_counts[str(response.status_code)] = status_counts.get(str(response.status_code), 0) + 1
        if 200 <= response.status_code < 300:
            rate_limit_observations["responses_2xx"] += 1
        elif response.status_code == 429:
            rate_limit_observations["responses_429"] += 1
            rate_limit_observations["responses_4xx"] += 1
        elif 400 <= response.status_code < 500:
            rate_limit_observations["responses_4xx"] += 1
        elif response.status_code >= 500:
            rate_limit_observations["responses_5xx"] += 1

    with httpx.Client(timeout=settings.request_timeout, follow_redirects=False, max_redirects=0) as client:
        token_a = authenticate(client, target, login_path, identity_a)
        token_b = authenticate(client, target, login_path, identity_b)
        if token_a and token_b:
            for endpoint in discovery.get("endpoints", []):
                resource = _resource_path(endpoint)
                if not resource or endpoint["method"] != "GET":
                    continue
                try:
                    url = safe_url(target, resource)
                    owner = client.get(url, headers={"Authorization": f"Bearer {token_a}"})
                    attacker = client.get(url, headers={"Authorization": f"Bearer {token_b}"})
                    record(owner)
                    record(attacker)
                    owner_body, attacker_body = _json(owner), _json(attacker)
                    same_resource = owner.status_code == 200 and attacker.status_code == 200 and owner_body == attacker_body
                    status = "confirmed" if same_resource else "not_vulnerable"
                    if status == "confirmed":
                        finding_id = "bola-" + uuid4().hex[:12]
                        findings.append(Finding(finding_id=finding_id, type="BOLA", status=status, severity="HIGH", confidence="HIGH", endpoint=endpoint["path"], method="GET", resource_identifier="1", evidence=redact({"owner_status": owner.status_code, "attacker_status": attacker.status_code, "resource_match": same_resource}), description="A second identity received the same protected resource."))
                        pocs.append(Poc(finding_id=finding_id, method="GET", url=url, headers=safe_headers(token_b), authentication_context="Use the attacker identity token; replace <REDACTED> locally."))
                    if isinstance(attacker_body, dict):
                        exposed = sorted(key for key in attacker_body if SENSITIVE.search(key))
                        if exposed:
                            finding_id = "exposure-" + uuid4().hex[:12]
                            findings.append(Finding(finding_id=finding_id, type="EXCESSIVE_DATA_EXPOSURE", status="probable", severity="HIGH", confidence="MEDIUM", endpoint=endpoint["path"], method="GET", resource_identifier="1", evidence={"sensitive_fields": exposed, "status": attacker.status_code}, description="The response contains fields that are commonly sensitive and should be reviewed."))
                            pocs.append(Poc(finding_id=finding_id, method="GET", url=url, headers=safe_headers(token_a), authentication_context="Use an authorized identity token; secrets are intentionally omitted."))
                except httpx.TimeoutException:
                    rate_limit_observations["timeouts"] += 1
                    log.warning("endpoint test timed out")
                except (httpx.HTTPError, ValueError) as exc:
                    log.warning("endpoint test failed: %s", type(exc).__name__)
        endpoint_urls = [safe_url(target, e["path"].replace("{id}", "1")) for e in discovery.get("endpoints", [])[:config["requests"]] if "{" in e["path"]]
        for url in endpoint_urls:
            try:
                response = client.get(url, headers=safe_headers(token_a))
                record(response)
                if response.status_code >= 500:
                    break
            except httpx.TimeoutException:
                rate_limit_observations["timeouts"] += 1
                break
            except httpx.HTTPError:
                break
    counts = {level: sum(1 for finding in findings if finding.severity == level) for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    risk = min(100, counts["CRITICAL"] * 30 + counts["HIGH"] * 20 + counts["MEDIUM"] * 10 + counts["LOW"] * 3)
    aborted = rate_limit_observations["responses_5xx"] > 0 or rate_limit_observations["timeouts"] > 0
    return {"scan_id": session_id, "status": "completed", "target": {"base_url": target, "openapi_version": discovery.get("version")}, "mode": mode, "summary": {"endpoints_tested": len(discovery.get("endpoints", [])), "tests_executed": requests_made, "vulnerabilities": len(findings)}, "score": {"value": risk, "label": "SentinelAPI Prototype Risk Score"}, "findings": findings, "pocs": pocs, "statistics": {"requests_made": requests_made, "duration_seconds": round(time.monotonic() - started, 3), "severity_counts": counts, "status_counts": status_counts, "rate_limit_observations": rate_limit_observations}, "safety": {"aborted": aborted, "reason": "target degradation or timeout observed" if aborted else None}}
