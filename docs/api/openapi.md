---
type: API Spec
title: OpenAPI Documentation
description: Backend API endpoints, auth flows, CSRF handling, rate limiting, and OpenAPI schema generation.
tags: [openapi, auth, endpoints, drf-spectacular, csrf]
timestamp: 2026-07-17
---

# OpenAPI

## Generated API Docs

The backend publishes generated OpenAPI documentation with `drf-spectacular`:

* `GET /api/schema/` returns the machine-readable OpenAPI schema.
* `GET /api/docs/swagger/` serves public Swagger UI for interactive browsing.
* `GET /api/docs/redoc/` serves public ReDoc reference documentation.

These routes are intentionally public in development and production. The schema
documents public API behavior, Django session-cookie authentication, and CSRF
expectations without exposing provider secrets, private environment values, or
operational stack details.

## Auth

Auth endpoints use Django session cookies for browser authentication. Mutating
auth endpoints verify Cap proof-of-work captcha tokens when captcha is enabled
on the backend. Password reset emails build confirmation links from
`FRONTEND_BASE_URL`.

Google social auth also uses Django session cookies. Google OAuth/OIDC token
exchange happens only on the backend; provider tokens are not returned to Nuxt or
stored in browser storage. Social auth starts and callbacks are throttled and use
generic user-facing failure redirects.

Human-facing auth response text, validation messages, and backend-generated auth
emails are localized from the HTTP `Accept-Language` header. The backend supports
`en` and `fr`; unsupported or missing language headers fall back to English.
Clients must not use translated `detail` or validation text for control flow.
Use stable response shapes, field names, HTTP status codes, and machine-readable
codes such as `EMAIL_VERIFICATION_REQUIRED` instead.

Browser clients must send Django's CSRF token on authenticated unsafe requests,
including `POST /api/auth/logout/`. Successful login and email verification
confirmation responses issue a `csrftoken` cookie for browser sessions. Beacon's
Nuxt frontend reads the `csrftoken` cookie through its shared backend API
transport and sends it as the `X-CSRFToken` header on unsafe API methods when
using session cookies.

Abuse-sensitive auth endpoints are rate limited. Login, reset, and verification
throttles key on submitted identifiers when present so repeated attacks against
the same account or token are limited across client IPs. Throttled requests return
`429 Too Many Requests`.

Account responses return a public account envelope. Signup creates an unverified
account and schedules a six-digit email verification code after the account
transaction commits; successful login requires the email address to be verified.
Google social signup is open: a verified Google email with no Beacon account
creates an account with a generated username and an unusable password, while a
verified Google email matching an existing Beacon account auto-links the Google
identity and logs that account in. Unverified provider email claims are never
used for email-based auto-linking.

Social auth is account authentication only. It is not wallet identity, Solana
account ownership proof, anti-sybil proof, or any claim about on-chain access.

```json
{
  "account": {
    "id": 1,
    "email": "user@example.com",
    "username": "readerone",
    "display_name": "Reader One",
    "wallet_address": null,
    "reputation_score": "0.00",
    "account_credit": "0.000000000",
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
  "email": "user@example.com",
  "username": "readerone",
  "display_name": "Reader One",
  "password": "correct horse battery staple",
  "password_confirmation": "correct horse battery staple",
  "captcha_token": "cap-jwt-token"
}
```

Responses:

* `201 Created` with the account envelope.
* `400 Bad Request` when input is invalid, the email or username already exists,
  password validation fails, or captcha verification fails.
* `429 Too Many Requests` when signup attempts exceed the configured throttle.

If the account transaction commits but the post-commit verification email send
fails, signup still returns `201 Created`. The user can request a replacement
code through `POST /api/auth/email-verification/request/`.

### `POST /api/auth/login/`

Authenticates an existing account with email-or-username and password. On
success, Django sets a session cookie and a `csrftoken` cookie.

Request body:

```json
{
  "identifier": "user@example.com",
  "password": "correct horse battery staple",
  "captcha_token": "cap-jwt-token"
}
```

Responses:

* `200 OK` with the account envelope.
* `400 Bad Request` with `{ "code": "EMAIL_VERIFICATION_REQUIRED", "email": "user@example.com" }`
  when credentials are valid but the account email is unverified.
* `400 Bad Request` when credentials are invalid or captcha verification fails.
* `429 Too Many Requests` when login attempts exceed the configured throttle.

### `POST /api/auth/email-verification/request/`

Requests a new email verification code. When the email belongs to an unverified
account, Beacon sends a six-digit numeric code that expires after 15 minutes.
The response is intentionally generic and does not reveal whether an account
exists for the email.

Request body:

```json
{
  "email": "user@example.com",
  "captcha_token": "cap-jwt-token"
}
```

Responses:

* `202 Accepted` with `{ "detail": "If an account exists, a verification code will be sent." }`.
* `400 Bad Request` when input is invalid or captcha verification fails.
* `429 Too Many Requests` when verification-code requests exceed the configured
  throttle.

Email verification resend uses Django's configured email backend synchronously.
If the backend raises a delivery error, the request can fail before returning the
generic `202 Accepted` response.

### `POST /api/auth/email-verification/confirm/`

Confirms a pending email verification code. Each code allows a configurable
number of failed confirmation attempts before the user must request a new code.
On success, Beacon marks the account email as verified, clears the stored OTP
hash and expiry, starts a Django session, and sets a `csrftoken` cookie.

Request body:

```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

Responses:

* `200 OK` with the account envelope.
* `400 Bad Request` when the code is invalid, expired, missing, malformed, or
  has exceeded the configured verification attempt limit.
* `429 Too Many Requests` when verification attempts exceed the configured
  request throttle.

### `POST /api/auth/logout/`

Clears the current Django session.

Responses:

* `204 No Content`.
* `403 Forbidden` when an authenticated session request omits a valid CSRF token.

### `GET /api/auth/me/`

Returns the current authenticated account.

Responses:

* `200 OK` with the account envelope.
* `403 Forbidden` when no authenticated session exists.

### `GET /api/auth/social/providers/`

Returns the enabled social auth providers. The response exposes public provider
metadata and start URLs only; it never exposes client secrets or provider tokens.

Responses:

* `200 OK` with provider metadata.

Example response:

```json
{
  "providers": [
    {
      "id": "google",
      "name": "Google",
      "start_url": "https://api.beacon.example/api/auth/social/google/start/",
      "enabled": true
    }
  ]
}
```

### `POST /api/auth/social/google/start/`

Starts Google OAuth/OIDC authorization for browser clients. The optional `next`
value must be a same-site relative path. Unsafe absolute, scheme-relative, or
non-root-relative values are rejected.

Request body:

```json
{
  "next": "/dashboard"
}
```

Responses:

* `200 OK` with `{ "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..." }`.
* `400 Bad Request` when `next` is unsafe.
* `429 Too Many Requests` when social auth starts exceed the configured throttle.
* `503 Service Unavailable` when Google OAuth is not configured on the backend.

### `GET /api/auth/social/google/callback/`

Handles Google's redirect callback. The backend validates state, exchanges the
authorization code for provider data, resolves or creates the Beacon account,
calls Django `login()`, issues a `csrftoken` cookie, and redirects back to Nuxt.

Successful callbacks redirect to the validated `next` path, defaulting to
`/dashboard`, with `social_auth=success`. Failed callbacks redirect to the login
page with `error=social_auth_failed`. Error redirects are intentionally generic
and do not reveal provider, state, token, or account-linking details.

Responses:

* `302 Found` to the Nuxt success destination when login succeeds.
* `302 Found` to the Nuxt login error destination when state validation, provider
  response, token exchange, or account resolution fails.

### `POST /api/auth/password-reset/`

Requests a password reset. When the email belongs to an account, Beacon sends a
reset link to that address using Django's email backend. The response is
intentionally generic and does not reveal whether an account exists for the
email.

Request body:

```json
{
  "email": "user@example.com",
  "captcha_token": "cap-jwt-token"
}
```

Responses:

* `202 Accepted` with `{ "detail": "If an account exists, password reset instructions will be sent." }`.
* `400 Bad Request` when input is invalid or captcha verification fails.
* `429 Too Many Requests` when reset requests exceed the configured throttle.

Password reset email delivery uses Django's configured email backend
synchronously. If the backend raises a delivery error for an existing account,
the request can fail before returning the generic `202 Accepted` response.

### `POST /api/auth/password-reset/confirm/`

Confirms a password reset using Django's uid/token pair and sets a new password.

Request body:

```json
{
  "uid": "MQ",
  "token": "set-password-token",
  "password": "new correct horse battery staple"
}
```

Responses:

* `200 OK` with `{ "detail": "Password has been reset." }`.
* `400 Bad Request` when the token is invalid or password validation fails.
* `429 Too Many Requests` when reset confirmation attempts exceed the configured
  throttle.

## Recommendation Lifecycle (Planned)

API endpoints for the recommendation lifecycle will follow after the backend
data model is approved and implemented. Planned surfaces include creating and
reactivating canonical recommendation pages, managing recommender stake
references, supporting/upvoting recommendations, bookmarking, following
curators, listing badges, and reading reputation or profile summaries.

These endpoints are not yet implemented and will be documented here once
designed.
