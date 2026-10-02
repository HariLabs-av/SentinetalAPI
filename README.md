# 🛡️ SentinelAPI

### Intelligent API Security Testing & Vulnerability Analysis Platform

**SentinelAPI** is an intelligent API security platform designed to automatically analyze APIs, discover security weaknesses, and generate structured evidence for vulnerabilities.

Modern applications rely heavily on APIs, but manually testing every endpoint for authorization flaws, data exposure, and configuration issues can be time-consuming. SentinelAPI aims to automate this process through a modular security-testing workflow.

---

## 🚀 Key Features

* 🔍 **API Endpoint Discovery**

  * Analyze API specifications and identify available endpoints.
  * Extract HTTP methods, parameters, request bodies, and authentication requirements.

* 🔐 **Authorization Testing**

  * Detect potential **Broken Object Level Authorization (BOLA/IDOR)** vulnerabilities.
  * Compare responses across different authorization contexts.

* 🕵️ **Sensitive Data Exposure Detection**

  * Identify potentially sensitive information returned by APIs.
  * Analyze response structures and exposed fields.

* ⚡ **Rate-Limit Analysis**

  * Perform controlled testing of API request limits.
  * Identify endpoints that may lack appropriate rate limiting.

* 🧠 **Intelligent Analysis**

  * Combine automated security checks with contextual analysis.
  * Reduce noisy results by correlating multiple observations.

* 📑 **Evidence-Based Findings**

  * Store request/response evidence for detected issues.
  * Provide structured vulnerability information instead of simple pass/fail results.

* 🧩 **Modular Architecture**

  * Individual security modules can be developed, tested, and extended independently.

---

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │   API / OpenAPI  │
                    │   Specification   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ API Discovery &  │
                    │    Parsing       │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │   Security Testing      │
                 │        Engine           │
                 └───────────┬─────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
      ┌───────────┐   ┌──────────────┐  ┌─────────────┐
      │   BOLA    │   │ Data Exposure│  │ Rate Limit  │
      │   Tester  │   │   Detector   │  │   Tester    │
      └─────┬─────┘   └──────┬───────┘  └──────┬──────┘
            │                │                  │
            └────────────────┼──────────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Evidence &       │
                    │ Confidence Layer │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Structured       │
                    │ Security Report  │
                    └──────────────────┘
```

---

## 🔄 How It Works

SentinelAPI follows a structured security-testing workflow:

### 1. API Input

The user provides an API specification or target API information.

Supported input can include an **OpenAPI/Swagger specification**.

### 2. API Discovery

SentinelAPI parses the API and identifies:

* Endpoints
* HTTP methods
* Parameters
* Request bodies
* Authentication requirements
* Possible object identifiers

### 3. Security Testing

The discovered endpoints are passed to specialized security modules.

For example:

```text
Endpoint
   │
   ├── Authorization Test
   ├── Sensitive Data Test
   └── Rate Limit Test
```

Each module focuses on a specific security problem.

### 4. Evidence Collection

Instead of simply reporting:

```text
VULNERABLE
```

SentinelAPI collects supporting evidence such as:

* Endpoint
* HTTP method
* Request information
* Response information
* Test performed
* Observed behavior
* Confidence level

### 5. Structured Results

The collected information is converted into structured findings that can be displayed in a dashboard or exported as a security report.

---

# 🔐 Security Checks

## BOLA / IDOR Detection

SentinelAPI can test whether an authenticated user can access objects belonging to another user.

Example:

```text
User A
   │
   │ GET /api/users/101
   ▼
Object 101
```

The system can then test whether the same authorization context can improperly access:

```text
GET /api/users/102
```

Unexpected access can indicate a potential authorization vulnerability.

> Testing should only be performed against APIs that you own or have explicit permission to assess.

---

## 🕵️ Sensitive Data Exposure

APIs sometimes return more information than the client actually needs.

For example:

```json
{
  "id": 101,
  "name": "John",
  "email": "john@example.com",
  "password_hash": "...",
  "internal_token": "..."
}
```

SentinelAPI can analyze responses for potentially sensitive fields and flag suspicious exposure for further review.

---

## ⚡ Rate-Limit Testing

APIs should generally protect sensitive endpoints from excessive requests.

SentinelAPI can perform controlled rate-limit checks and observe:

* HTTP status codes
* Response behavior
* Rate-limit headers
* Request thresholds
* Changes in server responses

The goal is to identify potentially unprotected endpoints without generating unnecessary load.

---

# 🧩 Project Structure

A possible project structure is:

```text
SentinelAPI/
│
├── README.md
├── requirements.txt
├── package.json
│
├── src/
│   ├── parser/
│   │   └── api_parser
│   │
│   ├── scanners/
│   │   ├── bola/
│   │   ├── data_exposure/
│   │   └── rate_limit/
│   │
│   ├── analyzer/
│   │   └── evidence_analyzer
│   │
│   ├── reporting/
│   │   └── report_generator
│   │
│   └── main
│
├── tests/
│   ├── bola/
│   ├── data_exposure/
│   └── rate_limit/
│
└── examples/
    └── sample_api.yaml
```

> The exact structure may vary depending on the implementation.

---

# 🛠️ Technology Stack

The project can be built using technologies such as:

| Component        | Technology                        |
| ---------------- | --------------------------------- |
| Backend          | Python / Node.js                  |
| API Processing   | OpenAPI / Swagger                 |
| Security Testing | Custom testing modules            |
| Analysis         | Rule-based + AI-assisted analysis |
| Data Format      | JSON                              |
| Frontend         | HTML / CSS / JavaScript           |
| Database         | Configurable                      |
| Version Control  | Git / GitHub                      |

---

# 📊 Example Finding

A SentinelAPI finding can follow a structured format:

```json
{
  "type": "BOLA",
  "severity": "High",
  "endpoint": "/api/users/{id}",
  "method": "GET",
  "confidence": 0.91,
  "description": "Potential unauthorized object access detected.",
  "evidence": {
    "tested_object": "102",
    "authorization_context": "User A",
    "response_status": 200
  }
}
```

This makes the result easier to:

* Review
* Store
* Display
* Export
* Integrate with other security tools

---

# 🎯 Goals

SentinelAPI aims to:

* Automate repetitive API security testing.
* Make API vulnerabilities easier to identify.
* Provide evidence-backed findings.
* Reduce false positives through contextual analysis.
* Provide a modular foundation for adding additional security checks.
* Make API security testing more accessible to developers.

---

# 🔮 Future Scope

Potential future improvements include:

* [ ] JWT security analysis
* [ ] API authentication testing
* [ ] SQL injection detection
* [ ] NoSQL injection detection
* [ ] SSRF detection
* [ ] Security misconfiguration detection
* [ ] GraphQL security testing
* [ ] API fuzzing
* [ ] CI/CD integration
* [ ] Automated security reports
* [ ] Dashboard and visualization
* [ ] More advanced AI-assisted vulnerability analysis

---

# ⚠️ Responsible Use

SentinelAPI is intended for **authorized security testing only**.

Do not use the platform to test APIs, applications, systems, or infrastructure without permission from the owner.

Security testing should be performed in controlled environments or against systems where you have explicit authorization.

---

# 👥 Team

**SentinelAPI**
API Security Testing & Analysis Platform

Built as a cybersecurity / software engineering project.

---

# 📄 License

Add your preferred license here.

For example:

```text
MIT License
```

---

## ⭐ Project Vision

> **SentinelAPI — Discover. Test. Analyze. Secure.**

The goal is to transform API security testing from a manual, repetitive process into an intelligent, evidence-driven workflow.

This repository is organized for GitHub:

```text
SentinelAPI/
├── backend/       FastAPI scanner, tests, docs, local demo target
├── frontend/      Static browser dashboard
├── targets/       Vulnerable and secure Spring Boot demo APIs
├── .env.example
└── README.md
```

Student ownership remains separated: Student 1 supplies the Java target APIs,
Student 2 owns this scanner backend, Student 3 owns AI interpretation, and
Student 4 owns the dashboard. The included frontend is an integration prototype.

The two demo target applications are available at:

```text
targets/vulnerable-api/
targets/secure-api/
```

Deploy them as separate Java services when hosting the complete demo. Set
`DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `JWT_SECRET`, and the platform-provided
`PORT` in each service; never use the local MySQL defaults in production.

## Local run

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
HOST=127.0.0.1 PORT=8000 python run.py
```

Frontend:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500`. For the teammate APIs, enter:

```text
Vulnerable: http://127.0.0.1:8081/v3/api-docs
Secure:     http://127.0.0.1:8082/v3/api-docs
```

Use the authorized demo credentials supplied with those APIs. The scanner
should report findings for the vulnerable target and a clean result for the
secure target.

## Optional AI remediation guidance

The backend endpoint is:

```http
POST /api/v1/scan/{scan_id}/ai-report
```

It sends only sanitized deterministic scan evidence to Gemini. It asks for
root cause, missing security control, remediation options, validation tests,
and limitations—not an automatically deployable patch. The scanner remains
the authority for findings and developers must review AI guidance.

Configure locally without committing the key:

```bash
export AI_PROVIDER='groq'
export GROQ_API_KEY='your-new-groq-key'
export GROQ_MODEL='openai/gpt-oss-120b'
```

Never expose AI provider keys in frontend code or GitHub. Any key pasted into chat,
source, screenshots, or a public repository must be revoked and replaced.

## Hosting

Deploy `backend/` as a Python web service using the start command:

```bash
python run.py
```

Set `HOST=0.0.0.0`, the platform-provided `PORT`, a specific
`SENTINELAPI_CORS_ORIGINS` value for the deployed frontend, and
`SENTINELAPI_ALLOW_PRIVATE_TARGETS=false` unless the deployment is explicitly
inside an authorized private test network. Deploy `frontend/` to a static
host and configure its backend URL for the deployed HTTPS API. Use HTTPS,
secret-manager environment variables, and a reverse proxy in production.

See `backend/docs/internal/` for the API contract, security model, AI boundary,
and local demo instructions.
