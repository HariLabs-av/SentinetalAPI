# API contract

All endpoints are under `/api/v1`.

`GET /health` returns `{"status":"ok","service":"sentinelapi-backend","contract_version":"1.0"}`.

`POST /discover` accepts `target_url` and optional `openapi_url`. It returns `session_id`, target, and discovery metadata. `POST /scan` accepts `session_id`, `mode`, `login_path`, `identity_a`, and `identity_b`, and returns a `ScanResult`. `GET /scan/{scan_id}` returns the same result. Validation errors use FastAPI's 422 shape; target/session errors use a JSON `detail` and HTTP 400/404.

Example scan request:

```json
{"session_id":"opaque-id","mode":"moderate","login_path":"/auth/login",
 "identity_a":{"username":"owner","password":"placeholder"},
 "identity_b":{"username":"other","password":"placeholder"}}
```

Results contain `summary`, prototype `score`, findings, placeholder PoCs, statistics, and safety state. Passwords and tokens are never part of the response.

The static frontend integration is in `/home/ladduji/SentinelFrontend` and
uses discovery before scan. It sends target credentials only in the scan
request; it does not persist or display tokens.
