import logging
import secrets
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .ai import AIConfigurationError, AIProviderError, generate_report
from .models import DiscoverRequest, ScanRequest, ScanResult
from .openapi import discover
from .scanner import scan
from .config import settings
from .security import TargetError, validate_target

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app = FastAPI(title="SentinelAPI Backend", version="1.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)
sessions: dict[str, dict[str, Any]] = {}
results: dict[str, ScanResult] = {}


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sentinelapi-backend", "contract_version": "1.0"}


@app.post("/api/v1/discover")
def create_discovery(request: DiscoverRequest) -> dict[str, Any]:
    try:
        target = validate_target(str(request.target_url))
        metadata = discover(target, str(request.openapi_url) if request.openapi_url else None)
    except (TargetError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session_id = secrets.token_urlsafe(24)
    sessions[session_id] = {"target": target, "discovery": metadata}
    return {"session_id": session_id, "target": target, "discovery": metadata, "status": "ready"}


@app.post("/api/v1/scan", response_model=ScanResult)
def create_scan(request: ScanRequest) -> ScanResult:
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="scan session not found")
    raw = scan(request.session_id, session["target"], session["discovery"], request.mode, request.login_path, request.identity_a.model_dump(), request.identity_b.model_dump())
    result = ScanResult.model_validate(raw)
    results[request.session_id] = result
    return result


@app.get("/api/v1/scan/{scan_id}", response_model=ScanResult)
def get_scan(scan_id: str) -> ScanResult:
    if scan_id not in results:
        raise HTTPException(status_code=404, detail="scan result not found")
    return results[scan_id]


@app.post("/api/v1/scan/{scan_id}/ai-report")
def create_ai_report(scan_id: str) -> dict[str, Any]:
    result = results.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="scan result not found")
    try:
        return generate_report(result.model_dump())
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
