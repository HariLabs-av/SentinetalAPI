# Architecture

`sentinelapi/main.py` exposes the API and in-memory session/result stores. `security.py` validates targets and same-origin paths. `openapi.py` discovers and parses JSON/YAML specifications. `scanner.py` authenticates two identities and performs BOLA, sensitive-field, and bounded observation tests. `models.py` is the external contract.

The in-memory store is intentionally suitable for the MVP and must be replaced with an expiring store before multi-process deployment.
