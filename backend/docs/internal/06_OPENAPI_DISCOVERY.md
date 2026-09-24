# OpenAPI discovery

An explicit `openapi_url` is preferred. Otherwise the backend checks `/openapi.json`, `/openapi.yaml`, `/swagger.json`, and `/v3/api-docs` without following redirects. Both OpenAPI and Swagger metadata are accepted. Paths, methods, parameters, response keys, and security schemes are exposed as discovery metadata. Missing or malformed documents produce `found: false` rather than crashing the API.
