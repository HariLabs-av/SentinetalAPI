"""Optional Student 3 AI adapter.

The scanner remains the authority for technical evidence. Gemini only
interprets the already-sanitized ScanResult and must not receive credentials or
raw authorization headers.
"""

import json
import logging
from typing import Any

import httpx

from .config import settings
from .models import AIReport
from .redaction import redact

log = logging.getLogger(__name__)

class AIConfigurationError(RuntimeError):
    """Raised when the optional AI integration is not configured."""


class AIProviderError(RuntimeError):
    """Raised when the configured AI provider cannot produce a report."""


def _ai_input(scan_result: dict[str, Any]) -> dict[str, Any]:
    safe = {
        "target": scan_result.get("target"),
        "mode": scan_result.get("mode"),
        "summary": scan_result.get("summary"),
        "score": scan_result.get("score"),
        "findings": scan_result.get("findings"),
        "pocs": scan_result.get("pocs"),
        "statistics": scan_result.get("statistics"),
        "safety": scan_result.get("safety"),
    }
    return redact(safe)


def generate_report(scan_result: dict[str, Any]) -> dict[str, Any]:
    if not settings.gemini_api_key:
        raise AIConfigurationError("GEMINI_API_KEY is not configured")

    prompt = (
        "You are Student 3's API-security remediation advisor. Interpret only "
        "the deterministic scanner evidence below. Do not invent vulnerabilities, "
        "credentials, tokens, source code, or exact patches. The scanner, not "
        "the AI, established each finding. For every finding, explain the "
        "root_cause, missing_security_control, recommended_fix, implementation_options, "
        "validation_tests, and limitations. For BOLA, explain object ownership "
        "authorization and do not assume a particular framework or data model. "
        "Return concise JSON with keys executive_summary, findings, remediation, "
        "and limitations.\n\n"
        + json.dumps(_ai_input(scan_result), separators=(",", ":"))
    )
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    try:
        response = httpx.post(
            url,
            params={"key": settings.gemini_api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            },
            timeout=settings.gemini_timeout,
        )
        if response.is_error:
            log.warning("Gemini request failed with HTTP %s", response.status_code)
            try:
                provider_error = response.json().get("error", {})
                message = provider_error.get("message") or provider_error.get("status")
            except ValueError:
                message = None
            safe_message = str(message or "request was rejected").replace(settings.gemini_api_key or "", "<REDACTED>")
            raise AIProviderError(f"Gemini rejected the request (HTTP {response.status_code}): {safe_message}")
        body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
    except AIProviderError:
        raise
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise AIProviderError("Gemini returned an unusable response") from exc

    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        report: Any = AIReport.model_validate(json.loads(cleaned)).model_dump()
    except json.JSONDecodeError:
        report = {"raw_text": text}
    except (TypeError, ValueError):
        report = {"raw_text": text, "validation_error": "Provider response did not match the guidance schema"}
    return {
        "provider": "gemini",
        "model": settings.gemini_model,
        "scan_id": scan_result.get("scan_id"),
        "report": report,
        "source": "sanitized deterministic ScanResult",
    }
