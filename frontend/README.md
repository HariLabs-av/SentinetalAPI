# SentinelAPI frontend integration

This is the integrated static frontend for the SentinelAPI FastAPI backend.
Start the backend at `http://127.0.0.1:8000`, then serve this directory over
HTTP (opening `index.html` directly also works in browsers that permit local
fetch requests):

```bash
cd /home/ladduji/SentinelFrontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500`. Enter the target's OpenAPI URL, for example:

```text
http://127.0.0.1:8081/v3/api-docs
```

The frontend calls:

1. `POST /api/v1/discover`
2. `POST /api/v1/scan`
3. Optional `POST /api/v1/scan/{scan_id}/ai-report` for Student 3 remediation guidance

The current UI collects authorized usernames/passwords because the backend
performs authentication itself. It does not collect or display bearer tokens.
AI remediation guidance is intentionally advisory. It explains missing
security controls and validation tests; it does not claim to generate a
universally safe deployable patch from HTTP evidence alone.

For a hosted backend, set `window.SENTINEL_API_BASE_URL` before `js/api.js` is
loaded, or replace its development default with the HTTPS backend URL. The
backend's development CORS policy currently permits browser integration; limit
origins before production deployment.
