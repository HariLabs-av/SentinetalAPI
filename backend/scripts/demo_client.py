"""Frontend/AI integration simulator for the local SentinelAPI MVP.

The script submits discovery and scan requests like a frontend would, then
formats the structured result like a minimal AI/report consumer would.
"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(url: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read())
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def ai_placeholder(result: dict) -> str:
    findings = result.get("findings", [])
    if not findings:
        return "AI placeholder: no findings require explanation."
    lines = ["AI placeholder report:"]
    for finding in findings:
        lines.append(
            f"- {finding['severity']} {finding['type']} on {finding['method']} "
            f"{finding['endpoint']}: {finding['description']}"
        )
    lines.append("Student 3 can add reviewed remediation guidance here; exact patches are not inferred from HTTP evidence.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an end-to-end SentinelAPI demo")
    parser.add_argument("--backend", default="http://127.0.0.1:8000", help="SentinelAPI backend URL")
    parser.add_argument("--target", default="http://127.0.0.1:8090", help="Fake target URL")
    parser.add_argument("--mode", choices=("easy", "moderate", "brutal"), default="moderate")
    args = parser.parse_args()

    backend = args.backend.rstrip("/")
    target = args.target.rstrip("/")
    health = request_json(f"{backend}/api/v1/health")
    discovery = request_json(
        f"{backend}/api/v1/discover",
        "POST",
        {"target_url": target, "openapi_url": f"{target}/openapi.json"},
    )
    scan = request_json(
        f"{backend}/api/v1/scan",
        "POST",
        {
            "session_id": discovery["session_id"],
            "mode": args.mode,
            "login_path": "/auth/login",
            "identity_a": {"username": "alice", "password": "alice"},
            "identity_b": {"username": "bob", "password": "bob"},
        },
    )
    print("Backend:", health["status"])
    print("Discovered endpoints:", len(discovery["discovery"]["endpoints"]))
    print("Scan status:", scan["status"])
    print("Findings:", scan["summary"]["vulnerabilities"])
    print("Score:", scan["score"]["value"])
    print(ai_placeholder(scan))
    print("\nStructured result:")
    print(json.dumps(scan, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Demo failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
