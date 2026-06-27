# Beacon API

Backend workspace for Beacon.

This workspace uses Django, Django REST Framework, and PostgreSQL for the Beacon backend. The Django project is named `beacon_api`.

## What Is Installed

The current Python dependencies are tracked in `requirements.txt`:

* Django 5.2.15
* Django REST Framework 3.17.1
* django-allauth 65.13.1
* django-cors-headers 4.9.0
* django-environ 0.14.0
* psycopg 3.3.4 with the binary libpq wheel extra
* requests 2.32.5, retained as the OAuth2 HTTP transport used by
  `django-allauth`
* PyJWT 2.10.1
* cryptography 46.0.3
* asgiref 3.11.1
* sqlparse 0.5.5
* typing_extensions 4.15.0

Development-only Python tools are tracked in `requirements-dev.txt`:

* Ruff 0.15.20
* pytest 9.1.1
* pytest-django 4.12.0
* factory_boy 3.3.3

## Docker Setup

Run these commands from `apps/api/`.

Make sure Docker Desktop or the Docker daemon is running first.

### 1. Configure Environment Variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

The default `.env.example` values are for local development only.

### 2. Build And Start Backend Services

```bash
docker compose up --build
```

This starts:

* Django API at `http://localhost:8000`
* PostgreSQL at `localhost:5432`

### 3. Run Migrations In Docker

In another terminal, from `apps/api/`:

```bash
docker compose run --rm api python manage.py migrate
```

### 4. Run Backend Tests In Docker

```bash
docker compose run --rm api pytest
```

### 5. Run Backend Linting In Docker

```bash
docker compose run --rm api ruff check .
```

## Virtual Environment Setup

The `.venv` workflow remains available for quick local development and editor integration.

Use Python 3.14.6 for local virtual environments. The pinned local version is
recorded in `.python-version`, and the backend Docker image uses the matching
`python:3.14.6-slim` runtime.

Run these commands from `apps/api/`.

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

A virtual environment is an isolated Python installation for this backend workspace. It keeps this project's Python packages separate from packages installed globally on your machine.

### 2. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

When activated, your terminal prompt usually shows `(.venv)`.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

For development, install the development tools too:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

The default `.env.example` values are for local development only.

### 5. Start PostgreSQL Only

If you run Django through `.venv`, PostgreSQL can still run through Docker Compose from this workspace:

Make sure Docker Desktop or the Docker daemon is running first.

```bash
docker compose up -d postgres
```

Check that the database is healthy:

```bash
docker compose ps
```

### 6. Run Migrations

```bash
.venv/bin/python manage.py migrate
```

### 7. Verify Django

```bash
python -m django --version
```

Expected version:

```text
5.2.15
```

### 8. Verify Django REST Framework

```bash
python - <<'PY'
import rest_framework
print(rest_framework.VERSION)
PY
```

Expected version:

```text
3.17.1
```

## Current Status

* Python virtual environment: `apps/api/.venv/`
* Backend Dockerfile: `apps/api/Dockerfile`
* Docker Compose services: `api` and `postgres`
* Dependency list: `apps/api/requirements.txt`
* Development dependency list: `apps/api/requirements-dev.txt`
* Django installed: yes
* Django REST Framework installed: yes
* PostgreSQL driver installed: yes
* Local PostgreSQL database: Docker Compose service in `apps/api/compose.yaml`
* Django project generated: yes, `beacon_api`
* Ruff installed: yes
* pytest installed: yes
* Django apps generated: yes, `accounts`
* Database configured: yes, through `DATABASE_URL`

## Quality Checks

Run these commands from `apps/api/`.

### Format Python Files

```bash
.venv/bin/ruff format .
```

### Lint Python Files

```bash
.venv/bin/ruff check .
```

### Auto-Fix Lint Issues

```bash
.venv/bin/ruff check --fix .
```

The root pre-commit hook runs Ruff only when staged Python files exist under `apps/api/`.

## Auth Configuration

The auth API uses Django session cookies, CSRF protection, optional reCAPTCHA,
email verification OTPs, password reset emails, Google social auth through
`django-allauth`, and cache-backed auth throttles.

Important environment variables:

* `FRONTEND_BASE_URL` controls password-reset confirmation links.
* `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and
  `GOOGLE_OAUTH_REDIRECT_URI` configure Google social auth. If the Google client
  ID or secret is missing, the social auth start endpoint returns `503 Service
  Unavailable`.
* `EMAIL_VERIFICATION_MAX_ATTEMPTS` limits failed attempts per OTP before the
  user must request a new code.
* `AUTH_SIGNUP_THROTTLE_RATE`, `AUTH_LOGIN_THROTTLE_RATE`,
  `AUTH_PASSWORD_RESET_THROTTLE_RATE`,
  `AUTH_PASSWORD_RESET_CONFIRM_THROTTLE_RATE`,
  `AUTH_EMAIL_VERIFICATION_REQUEST_THROTTLE_RATE`, and
  `AUTH_EMAIL_VERIFICATION_CONFIRM_THROTTLE_RATE` tune auth throttles. Login,
  reset, and verification throttles key on submitted identifiers when present so
  repeated attacks against the same account are limited across client IPs.
* `AUTH_SOCIAL_START_THROTTLE_RATE` and
  `AUTH_SOCIAL_CALLBACK_THROTTLE_RATE` tune Google social auth start and callback
  throttles.
* `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`,
  `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, and
  `SECURE_HSTS_PRELOAD` enable production cookie and HTTPS hardening.
* `DEFAULT_FROM_EMAIL` sets the sender for verification and password-reset
  emails unless a custom email backend overrides it.

Signup creates the account transactionally and schedules the initial verification
email after commit. If that post-commit email send fails, signup still returns
`201 Created`; the user can request a replacement code from the verification
resend endpoint. Verification resend and password reset requests send email
synchronously through Django's configured email backend, so backend email errors
can fail those requests even though their response bodies remain generic when the
email backend succeeds.

Before production or public traffic, set `RECAPTCHA_ENABLED=true` with a valid
`RECAPTCHA_SECRET_KEY` and configure the Nuxt frontend with
`NUXT_PUBLIC_RECAPTCHA_SITE_KEY` so browser auth submissions send reCAPTCHA v2
Invisible tokens.

Browser clients using session cookies must send Django's CSRF token on
authenticated unsafe requests. Successful login and email verification
confirmation responses issue a `csrftoken` cookie; the Nuxt frontend reads that
cookie through its shared backend API transport and sends it as `X-CSRFToken` on
unsafe API methods.

Google social auth exchanges provider tokens only on the backend through
`django-allauth`'s Google adapter and OAuth2 client, and returns no provider token
data to Nuxt. Beacon's callback wrapper handles only Beacon-specific redirects,
session login, strict normalized identity validation, and account resolution; it
does not perform direct provider HTTP requests. `requests` remains a direct
dependency because allauth's OAuth2 client uses it for provider token and userinfo
HTTP transport. A verified Google email can auto-link to an existing Beacon
account or create a new social-only account with a generated username. This is
account authentication only; it is not wallet identity or proof of Solana account
ownership.

## Tests

Run backend tests with the portable PostgreSQL runner from `apps/api/`:

```bash
./scripts/test-postgres.sh
```

Pass pytest arguments through the runner for targeted checks:

```bash
./scripts/test-postgres.sh tests/test_auth_api.py
```

The runner starts the Docker Compose PostgreSQL service, waits for readiness,
and runs pytest with a known `DATABASE_URL`. If `apps/api/.venv` is not present,
it runs pytest inside the `api` container instead. This is the recommended path
because it does not depend on a machine-level PostgreSQL install.

Docker Desktop or the Docker daemon must be running first. If the runner reports
that Docker is not reachable, start Docker Desktop and rerun the command. Avoid
using plain `.venv/bin/pytest` as the default local workflow unless PostgreSQL is
already running at the configured `DATABASE_URL`.

You can also run tests fully inside Docker:

```bash
docker compose run --rm api pytest
```

Plain `.venv` pytest runs are available when a compatible PostgreSQL server is
already running at the configured `DATABASE_URL`:

```bash
.venv/bin/pytest
```

The current backend test suite contains smoke tests for Django settings, PostgreSQL configuration, Django REST Framework installation, and password/session auth API behavior. It covers signup, login, logout, profile reads, password reset, email verification OTPs, Google social auth start/callback behavior, captcha gating, CSRF enforcement, throttling, and account uniqueness edge cases.

Backend tests are intentionally not part of the pre-commit hook. They should be run manually during development and later in CI.

## Database Commands

Run from `apps/api/`.

```bash
docker compose up --build
docker compose run --rm api python manage.py migrate
docker compose run --rm api pytest
docker compose run --rm api ruff check .
docker compose up -d postgres
./scripts/test-postgres.sh
docker compose ps
docker compose down
```

To remove the local database volume and all stored data:

```bash
docker compose down -v
```

## Next Backend Step

Expand the API domain model after deciding the initial MVP entities beyond email-based account access.
