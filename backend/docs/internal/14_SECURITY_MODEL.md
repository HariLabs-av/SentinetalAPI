# Security model

Targets accept only HTTP(S), reject URL credentials and fragments, reject cross-origin paths and redirects, enforce request timeouts and response-size limits, and can disable private/loopback networks through `SENTINELAPI_ALLOW_PRIVATE_TARGETS=false`. Localhost remains available for the default sandbox workflow.

The scanner uses bounded request counts and workers per mode. `brutal` is a UI name, not an unlimited denial-of-service mode. Target degradation (5xx responses or request errors) stops observation. Logs use type-level errors and never log credential values. Results use `<REDACTED>` placeholders.
