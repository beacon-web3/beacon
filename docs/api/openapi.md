# OpenAPI

## Auth

Auth endpoints use Django session cookies for browser authentication. Mutating
auth endpoints verify reCAPTCHA v2 Invisible tokens when captcha is enabled on
the backend. Password reset emails build confirmation links from
`FRONTEND_BASE_URL`.

Browser clients must send Django's CSRF token on authenticated unsafe requests,
including `POST /api/auth/logout/`. Beacon's Nuxt frontend should read the
`csrftoken` cookie and send it as the `X-CSRFToken` header when using session
cookies.

Abuse-sensitive auth endpoints are rate limited by client IP. Throttled requests
return `429 Too Many Requests`.

Account responses return a public account envelope. Signup creates an unverified
account and sends a six-digit email verification code; successful login requires
the email address to be verified.

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
  "recaptcha_token": "recaptcha-v2-invisible-token"
}
```

Responses:

* `201 Created` with the account envelope.
* `400 Bad Request` when input is invalid, the email or username already exists,
  password validation fails, or captcha verification fails.
* `429 Too Many Requests` when signup attempts exceed the configured throttle.

### `POST /api/auth/login/`

Authenticates an existing account with email-or-username and password. On
success, Django sets a session cookie.

Request body:

```json
{
  "identifier": "user@example.com",
  "password": "correct horse battery staple",
  "recaptcha_token": "recaptcha-v2-invisible-token"
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
  "recaptcha_token": "recaptcha-v2-invisible-token"
}
```

Responses:

* `202 Accepted` with `{ "detail": "If an account exists, a verification code will be sent." }`.
* `400 Bad Request` when input is invalid or captcha verification fails.
* `429 Too Many Requests` when verification-code requests exceed the configured
  throttle.

### `POST /api/auth/email-verification/confirm/`

Confirms a pending email verification code. Each code allows a configurable
number of failed confirmation attempts before the user must request a new code.
On success, Beacon marks the account email as verified, clears the stored OTP
hash and expiry, and starts a Django session.

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

### `POST /api/auth/password-reset/`

Requests a password reset. When the email belongs to an account, Beacon sends a
reset link to that address using Django's email backend. The response is
intentionally generic and does not reveal whether an account exists for the
email.

Request body:

```json
{
  "email": "user@example.com",
  "recaptcha_token": "recaptcha-v2-invisible-token"
}
```

Responses:

* `202 Accepted` with `{ "detail": "If an account exists, password reset instructions will be sent." }`.
* `400 Bad Request` when input is invalid or captcha verification fails.
* `429 Too Many Requests` when reset requests exceed the configured throttle.

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
