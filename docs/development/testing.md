# Testing

Beacon uses separate testing tools for frontend and backend while package managers remain app-local.

## Frontend

Frontend end-to-end tests use Playwright in `apps/web/`.

Run from `apps/web/`:

```bash
pnpm exec playwright install chromium
pnpm test:e2e
pnpm test:e2e:ui
```

Current frontend test files live in:

```text
apps/web/tests/e2e/
```

The current E2E tests verify that the home page loads in Chromium, the landing
page fits narrow mobile screens without horizontal overflow, the French route
loads with LTR direction, and signup/login/email-verification/password-reset
forms submit to the password auth API contract. Auth E2E coverage also checks
CSRF header attachment, reCAPTCHA token inclusion, password reset confirmation
request shape, and weak-password blocking. Playwright starts the Nuxt dev server
automatically through `playwright.config.ts`.

## Backend

Backend tests use pytest in `apps/api/`.

Run PostgreSQL-backed tests with the portable `.venv` runner from `apps/api/`:

```bash
cd apps/api
./scripts/test-postgres.sh
```

Pass pytest arguments through the runner for targeted checks:

```bash
./scripts/test-postgres.sh tests/test_auth_api.py
```

The runner starts the Docker Compose PostgreSQL service, waits for readiness,
and runs pytest with a known `DATABASE_URL`. If `apps/api/.venv` is not present,
it runs pytest inside the `api` container instead. Use it instead of relying on
a machine-level PostgreSQL service at `localhost:5432`.

Docker Desktop or the Docker daemon must be running before invoking the runner.
If the runner prints `Docker is not running or is not reachable`, start Docker
Desktop and retry the same command. Do not use a plain `.venv/bin/pytest` run as
the default local workflow unless PostgreSQL is already listening at the
configured `DATABASE_URL`.

You can also run tests fully inside Docker from `apps/api/`:

```bash
docker compose run --rm api pytest
```

Plain `.venv` pytest runs are available when a compatible PostgreSQL server is
already running at the configured `DATABASE_URL`:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
.venv/bin/pytest
```

Current backend test files live in:

```text
apps/api/tests/
```

The current backend tests verify Django settings, PostgreSQL configuration,
Django REST Framework installation, password signup/login session behavior,
password reset email and confirmation behavior, captcha failure handling, CSRF
enforcement, CSRF cookie issuance for session-establishing auth responses,
throttling, and account uniqueness edge cases.

## What To Test Later

Backend tests should cover:

* Reward calculation rules
* Staking rules
* Recommendation lifecycle
* Django models
* Django REST Framework serializers and views
* API permissions

Frontend E2E tests should cover:

* Main page loads
* Navigation
* Book discovery flows
* Recommendation creation flows
* Supporting or staking on recommendations

## Pre-Commit Policy

Tests are not run by the pre-commit hook because they can be slower than linting and formatting.

Use pre-commit for fast staged-file checks only. Run tests manually during development and later through CI.
