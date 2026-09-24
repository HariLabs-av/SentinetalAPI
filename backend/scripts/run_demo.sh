#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "Starting fake target on http://127.0.0.1:8090..."
TARGET_PID=""
if curl --silent --fail --max-time 2 http://127.0.0.1:8090/openapi.json >/dev/null; then
  echo "Fake target is already running; reusing it."
else
  python3 scripts/fake_target.py &
  TARGET_PID=$!
  trap '[ -z "$TARGET_PID" ] || kill "$TARGET_PID" 2>/dev/null || true' EXIT
  sleep 1
  if ! curl --silent --fail --max-time 2 http://127.0.0.1:8090/openapi.json >/dev/null; then
    echo "Port 8090 is occupied, but it is not responding as the fake target." >&2
    exit 1
  fi
fi

echo "The Python backend must already be running at http://127.0.0.1:8000."
python3 scripts/demo_client.py "$@"
