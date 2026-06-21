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

The current E2E tests verify that the home page loads in Chromium, the Persian route sets RTL direction, and signup/login forms submit to the auth API. Playwright starts the Nuxt dev server automatically through `playwright.config.ts`.

## Backend

Backend tests use pytest in `apps/api/`.

Run with Docker from `apps/api/`:

```bash
docker compose run --rm api pytest
```

Or run with `.venv` from `apps/api/`:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
.venv/bin/pytest
```

Current backend test files live in:

```text
apps/api/tests/
```

The current backend tests verify Django settings, PostgreSQL configuration, Django REST Framework installation, and the email-only signup/login API behavior.

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
