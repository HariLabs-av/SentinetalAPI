# SentinelAPI Backend

SentinelAPI is an authorized sandbox API-security scanner. The repository root contains this backend and the integrated static frontend; Student 1's Spring Boot targets remain separate.

## Run on Fedora

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

The API listens on `http://127.0.0.1:8000`. Private and localhost targets are enabled by default for local fixtures. Set `SENTINELAPI_ALLOW_PRIVATE_TARGETS=false` for a deployment that must not reach private networks. Requests have timeouts, bounded response sizes, no-follow redirects, and bounded scan modes.

For hosting, set `HOST=0.0.0.0`, `PORT`, `SENTINELAPI_CORS_ORIGINS`, and
`SENTINELAPI_ALLOW_PRIVATE_TARGETS=false` through the platform environment.

## API

* `GET /api/v1/health`
* `POST /api/v1/discover` with `{"target_url":"http://localhost:8080","openapi_url":"http://localhost:8080/openapi.json"}`
* `POST /api/v1/scan` with a discovery `session_id`, two authorized identities, and `mode` (`easy`, `moderate`, or `brutal`)
* `GET /api/v1/scan/{session_id}`
* `POST /api/v1/scan/{session_id}/ai-report` (optional Student 3 Gemini integration)

Discovery stores only target metadata and an opaque session ID. Credentials are used transiently for the scan and are not returned in results. Scan results contain sanitized evidence and placeholder PoCs.

## Test

```bash
pytest -q
```

The scanner expects an OpenAPI/Swagger document and performs dual-identity GET checks for path resources, sensitive-field heuristics, and a bounded request observation. Results include HTTP status counts, 2xx/4xx/429/5xx/timeout observations, and a safety-abort state. It is a prototype risk score, not CVSS.

The optional AI remediation-guidance endpoint requires `GEMINI_API_KEY`. Set it only through the
environment; never commit it or place it in frontend code. The endpoint sends
only the sanitized structured scan result to Gemini. Without the key it returns
HTTP 503 and the scanner continues to work normally.

For a fallback target API that can be used before Student 1's Spring Boot APIs are ready, see `fallback-target/`.

For a no-Java end-to-end frontend/AI integration simulation, see `scripts/run_demo.sh` and `docs/internal/17_LOCAL_DEMO.md`.

See `docs/internal/05_API_CONTRACT.md` and `docs/internal/14_SECURITY_MODEL.md` before integrating the frontend or AI layer.
