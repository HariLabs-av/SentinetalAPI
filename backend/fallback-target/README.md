# Fallback target API

This dependency-free Java HTTP server is a backup demonstration target only. It is not Student 1's Spring Boot implementation. It exposes intentionally vulnerable and secure paths so the Python scanner can be demonstrated before the official APIs exist.

Run it with a JDK:

```bash
cd fallback-target
javac --add-modules jdk.httpserver Main.java
java --add-modules jdk.httpserver Main
```

It listens on `http://127.0.0.1:8090`. Login credentials are `alice/alice` and `bob/bob`. Discover it from the Python backend using `http://127.0.0.1:8090/openapi.json`.

`/api/vulnerable/users/{id}` returns Alice's record to both identities and demonstrates BOLA plus sensitive-field exposure. `/api/secure/users/{id}` returns the record only to Alice. The fallback target is suitable for local testing; use a reverse proxy and HTTPS before any hosted demonstration, and only expose it on an authorized environment.
