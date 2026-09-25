# SentinelAPI Secure API

This is the **secure counterpart** to `vulnerable-api` for the SentinelAPI hackathon demo.

Both apps expose the same basic business endpoints so the scanner can compare behavior.
The secure version fixes the two main vulnerabilities we introduced in the sandbox:

- **BOLA / IDOR**: every object lookup checks that the authenticated user owns the object.
- **Excessive data exposure**: API response DTOs never include `passwordHash` or other authentication secrets.

## Run

Requirements:
- Java 25
- Maven
- MySQL running locally

From this folder:

```bash
mvn spring-boot:run
```

The secure API runs on:

```text
http://localhost:8082
```

Swagger UI:

```text
http://localhost:8082/swagger-ui.html
```

OpenAPI JSON:

```text
http://localhost:8082/v3/api-docs
```

OpenAPI YAML:

```text
http://localhost:8082/v3/api-docs.yaml
```

The default local database is `sentinelapi_secure_demo`.

## Demo users

```text
alice / alice123
bob   / bob123
```

Demo orders:

```text
101 -> Alice
102 -> Bob
```

## Secure BOLA behavior

Alice's token can read order 101:

```http
GET /api/orders/101
Authorization: Bearer <ALICE_TOKEN>
```

Alice's token cannot read Bob's order 102:

```http
GET /api/orders/102
Authorization: Bearer <ALICE_TOKEN>
```

The secure API returns `403 Forbidden` for that unauthorized object access.

## Data exposure behavior

`GET /api/users` returns only:

```json
{
  "id": 1,
  "username": "alice",
  "fullName": "Alice Sharma"
}
```

The stored BCrypt password hash is deliberately **not** part of the response DTO.

## SentinelAPI demo

Use the scanner against:

```text
Target URL:    http://localhost:8082
OpenAPI URL:   http://localhost:8082/v3/api-docs
```

For BOLA testing, use Alice's JWT and object IDs `101` and `102`.

Only run the scanner against systems you own or are explicitly authorized to test.
# Render deployment

Create a Render Docker web service with root directory `targets/secure-api`.
The included Dockerfile builds and starts the API on Render's `PORT`.
