# Local demo harness

This harness lets the team demonstrate the Student 2 backend before Student 1's
Spring Boot APIs exist. It has three parts:

1. `scripts/fake_target.py` is a local, dependency-free target with vulnerable
   and secure endpoints.
2. `scripts/demo_client.py` behaves like a minimal Student 4 frontend client:
   it calls health, discovery, and scan.
3. The client's `ai_placeholder` consumes the structured result like a minimal
   Student 3 integration. It is intentionally not the AI implementation.

Start the backend in one terminal:

```bash
cd /home/ladduji/SentinentalBackend
source .venv/bin/activate
python run.py
```

Run the complete local demonstration in another:

```bash
cd /home/ladduji/SentinentalBackend
bash scripts/run_demo.sh
```

If the fake target is already running on port `8090`, the script reuses it.
Stop an old target manually with `Ctrl+C` in its terminal, or use another
`FAKE_TARGET_PORT` only when running the fixture directly.

Use a different backend host when needed:

```bash
bash scripts/run_demo.sh --backend http://127.0.0.1:8000 --mode easy
```

The demo uses `alice/alice` and `bob/bob`. The vulnerable endpoint returns
Alice's resource to both identities and includes `password_hash`, so the result
should contain BOLA and exposure findings. The secure endpoint denies Bob.
Everything is local and deterministic; do not expose this fixture publicly.
