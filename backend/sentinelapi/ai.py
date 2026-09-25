"""Optional Student 3 AI adapter.

The scanner remains the authority for technical evidence. The provider only
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
    provider = settings.ai_provider
    if provider == "groq":
        api_key = settings.groq_api_key
        model = settings.groq_model
        timeout = settings.groq_timeout
        url = "https://api.groq.com/openai/v1/chat/completions"
        request_kwargs = {
            "headers": {"Authorization": f"Bearer {api_key}"},
            "json": {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        }
    elif provider == "gemini":
        api_key = settings.gemini_api_key
        model = settings.gemini_model
        timeout = settings.gemini_timeout
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        request_kwargs = {
            "params": {"key": api_key},
            "json": {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            },
        }
    else:
        raise AIConfigurationError("AI_PROVIDER must be 'groq' or 'gemini'")
    if not api_key:
        raise AIConfigurationError(f"{provider.upper()} API key is not configured")
    try:
        response = httpx.post(url, timeout=timeout, **request_kwargs)
        if response.is_error:
            log.warning("%s request failed with HTTP %s", provider, response.status_code)
            try:
                provider_error = response.json().get("error", {})
                message = provider_error.get("message") or provider_error.get("status")
            except ValueError:
                message = None
            safe_message = str(message or "request was rejected").replace(api_key, "<REDACTED>")
            raise AIProviderError(f"{provider.title()} rejected the request (HTTP {response.status_code}): {safe_message}")
        body = response.json()
        if provider == "groq":
            text = body["choices"][0]["message"]["content"]
        else:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
    except AIProviderError:
        raise
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise AIProviderError(f"{provider.title()} returned an unusable response") from exc

    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        decoded: Any = json.loads(cleaned)
        # Some OpenAI-compatible providers return a JSON object encoded as a
        # JSON string even when response_format=json_object is requested.
        if isinstance(decoded, str):
            decoded = json.loads(decoded)
        report: Any = AIReport.model_validate(decoded).model_dump()
    except json.JSONDecodeError:
        report = {"raw_text": text}
    except (TypeError, ValueError):
        report = {"raw_text": text, "validation_error": "Provider response did not match the guidance schema"}
    return {
        "provider": provider,
        "model": model,
        "scan_id": scan_result.get("scan_id"),
        "report": report,
        "source": "sanitized deterministic ScanResult",
    }
