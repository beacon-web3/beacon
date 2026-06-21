# OpenAPI

## Auth

Current auth endpoints are intentionally minimal and email-only. They return an account envelope:

```json
{
  "account": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-06-03T00:00:00Z",
    "last_login_at": null
  }
}
```

### `POST /api/auth/signup/`

Creates a new account.

Request body:

```json
{
  "email": "user@example.com"
}
```

Responses:

* `201 Created` with the account envelope.
* `400 Bad Request` when the email is invalid or already exists.

### `POST /api/auth/login/`

Marks an existing account as logged in by updating `last_login_at`.

Request body:

```json
{
  "email": "user@example.com"
}
```

Responses:

* `200 OK` with the account envelope.
* `400 Bad Request` when the email is invalid or no account exists.
