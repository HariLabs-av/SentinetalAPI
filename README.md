# SentinelAPI

SentinelAPI is an authorized, sandbox-focused API vulnerability scanner for
the AmiHacks Problem Statement 3 prototype. It discovers OpenAPI/Swagger
documents, performs bounded dual-identity checks, detects basic BOLA and
sensitive-field exposure, and returns explainable structured evidence.

This repository is organized for GitHub:

```text
SentinelAPI/
├── backend/       FastAPI scanner, tests, docs, local demo target
├── frontend/      Static browser dashboard
├── targets/       Vulnerable and secure Spring Boot demo APIs
├── .env.example
└── README.md
```

Student ownership remains separated: Student 1 supplies the Java target APIs,
Student 2 owns this scanner backend, Student 3 owns AI interpretation, and
Student 4 owns the dashboard. The included frontend is an integration prototype.

The two demo target applications are available at:

```text
targets/vulnerable-api/
targets/secure-api/
```

Deploy them as separate Java services when hosting the complete demo. Set
`DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `JWT_SECRET`, and the platform-provided
`PORT` in each service; never use the local MySQL defaults in production.

## Local run

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
HOST=127.0.0.1 PORT=8000 python run.py
```

Frontend:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500`. For the teammate APIs, enter:

```text
Vulnerable: http://127.0.0.1:8081/v3/api-docs
Secure:     http://127.0.0.1:8082/v3/api-docs
```

Use the authorized demo credentials supplied with those APIs. The scanner
should report findings for the vulnerable target and a clean result for the
secure target.

## Optional AI remediation guidance

The backend endpoint is:

```http
POST /api/v1/scan/{scan_id}/ai-report
```

It sends only sanitized deterministic scan evidence to Gemini. It asks for
root cause, missing security control, remediation options, validation tests,
and limitations—not an automatically deployable patch. The scanner remains
the authority for findings and developers must review AI guidance.

Configure locally without committing the key:

```bash
export AI_PROVIDER='groq'
export GROQ_API_KEY='your-new-groq-key'
export GROQ_MODEL='llama-3.3-70b-versatile'
```

Never expose AI provider keys in frontend code or GitHub. Any key pasted into chat,
source, screenshots, or a public repository must be revoked and replaced.

## Hosting

Deploy `backend/` as a Python web service using the start command:

```bash
python run.py
```

Set `HOST=0.0.0.0`, the platform-provided `PORT`, a specific
`SENTINELAPI_CORS_ORIGINS` value for the deployed frontend, and
`SENTINELAPI_ALLOW_PRIVATE_TARGETS=false` unless the deployment is explicitly
inside an authorized private test network. Deploy `frontend/` to a static
host and configure its backend URL for the deployed HTTPS API. Use HTTPS,
secret-manager environment variables, and a reverse proxy in production.

See `backend/docs/internal/` for the API contract, security model, AI boundary,
and local demo instructions.
