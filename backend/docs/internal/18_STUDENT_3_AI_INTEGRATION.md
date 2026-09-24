# Student 3 AI integration

Student 3's extension point is:

```http
POST /api/v1/scan/{scan_id}/ai-report
```

The scan must already be completed. The backend sends Gemini only the
sanitized `target`, `mode`, `summary`, `score`, `findings`, `pocs`, `statistics`,
and `safety` fields. Credentials, passwords, bearer tokens, cookies, and raw
authorization headers are not sent. The scanner remains the authority for
whether evidence supports a finding; Gemini interprets that evidence.

Configure the provider locally:

```bash
export GEMINI_API_KEY='your-key'
export GEMINI_MODEL='gemini-2.5-flash'
```

Never commit the key, put it in a URL, or expose it to the frontend. The
frontend should call this backend endpoint after displaying the deterministic
scan result. The response currently returns provider/model metadata and the generated
report text. Student 3 should evolve this into validated remediation guidance:
root cause, missing control, implementation options, validation tests, and
limitations. Exact Java/Spring patch generation is out of scope because HTTP
evidence does not contain enough source context to produce a safe deployable
change.

Calling this endpoint sends scan metadata to Google Gemini. Use it only with
authorized targets and team-approved data-sharing settings.

If Gemini returns HTTP 401/403, rotate the key and restart the backend. If it
returns HTTP 404, set `GEMINI_MODEL` to a model enabled for that key. The API
key is never included in error responses or logs.
