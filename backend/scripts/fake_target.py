"""Local fake target API for SentinelAPI demonstrations.

This is deliberately not a production API. It is a dependency-free fixture that
provides vulnerable and secure paths for testing the scanner before Student 1's
Spring Boot APIs are available.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlparse


PORT = int(os.getenv("FAKE_TARGET_PORT", "8090"))


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/openapi.json", "/swagger.json"}:
            self._json(200, {
                "openapi": "3.0.0",
                "info": {"title": "SentinelAPI Fake Target", "version": "1.0"},
                "paths": {
                    "/api/vulnerable/users/{id}": {"get": {"responses": {"200": {"description": "user"}}}},
                    "/api/secure/users/{id}": {"get": {"responses": {"200": {"description": "user"}}}},
                },
            })
            return
        if path == "/api/vulnerable/users/1":
            self._user_response(200)
            return
        if path == "/api/secure/users/1":
            token = self.headers.get("Authorization", "")
            self._user_response(200 if "alice-demo-token" in token else 403)
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/auth/login":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            self._json(400, {"error": "invalid JSON"})
            return
        username = body.get("username")
        password = body.get("password")
        if username in {"alice", "bob"} and password == username:
            self._json(200, {"token": f"{username}-demo-token"})
            return
        self._json(401, {"error": "invalid credentials"})

    def _user_response(self, status: int) -> None:
        if status != 200:
            self._json(status, {"error": "forbidden"})
            return
        self._json(status, {
            "id": 1,
            "username": "alice",
            "email": "alice@example.test",
            "password_hash": "fixture-only",
        })

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Fake target listening at http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
