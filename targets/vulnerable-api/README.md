# SentinelAPI Vulnerable API

An intentionally vulnerable Spring Boot API used only as a **local sandbox** for the SentinelAPI hackathon project.

## Stack

- Java 25
- Spring Boot 4.0.6
- Spring Web
- Spring Security
- Spring Data JPA
- MySQL
- JJWT 0.13.0
- springdoc-openapi 3.1.1

## Why this exists

This API is the controlled target that SentinelAPI scans. It deliberately contains:

1. **BOLA/IDOR** on `GET /api/orders/{id}`: authenticated users can fetch another user's order by changing the object ID.
2. **Over-permissive list endpoint** on `GET /api/orders`: any authenticated user can see all demo orders.
3. **Excessive Data Exposure** on `GET /api/users`: password hashes are intentionally included in the JSON response.
4. **BOLA/IDOR-style user lookup** on `GET /api/users/{id}`: object-level ownership is not checked.

Do not deploy this application to a real or public environment.

## Demo accounts

| Username | Password | Expected user |
|---|---|---|
| alice | alice123 | Alice |
| bob | bob123 | Bob |

The application seeds two users and two orders when the database is empty:

- Alice → order 101 → Laptop Stand → ₹500
- Bob → order 102 → Mechanical Keyboard → ₹900

The demo deliberately uses fixed IDs: users 1/2 and orders 101/102, so the BOLA demo and scanner request are deterministic.

## Run

Create the database if needed:

```sql
CREATE DATABASE sentinelapi_demo;
```

Then make sure MySQL is running and run:

```bash
cd vulnerable-api
mvn spring-boot:run
```

Or run `VulnerableApiApplication` from IntelliJ.

## OpenAPI / Swagger

After startup:

- Swagger UI: http://localhost:8081/swagger-ui.html
- OpenAPI JSON: http://localhost:8081/v3/api-docs
- OpenAPI YAML: http://localhost:8081/v3/api-docs.yaml

The SentinelAPI scanner can use the OpenAPI JSON URL directly.

## Login

```http
POST http://localhost:8081/auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "alice123"
}
```

The response contains a JWT:

```json
{
  "token": "...",
  "username": "alice",
  "userId": 1
}
```

Use it like:

```http
Authorization: Bearer <TOKEN>
```

## Manual BOLA demonstration

1. Login as Alice.
2. Call `GET /api/orders/1` (or the Alice order ID shown in your DB).
3. Then call the Bob order ID using the **same Alice token**.
4. The API still returns Bob's order.

That is the behavior SentinelAPI should flag as BOLA.

## Scanner request

The scanner can use:

```json
{
  "targetUrl": "http://localhost:8081",
  "openApiSpec": "http://localhost:8081/v3/api-docs",
  "checks": ["BOLA"],
  "headers": {},
  "bola": {
    "userToken": "<ALICE_JWT>",
    "objectIds": ["<ALICE_ORDER_ID>", "<BOB_ORDER_ID>"],
    "objectIdParameter": "id"
  }
}
```
