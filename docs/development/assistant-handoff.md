# Assistant Handoff

This document tracks implementation context so a future assistant or developer can quickly understand the current repository state and continue work without rediscovering decisions.

## Current Status

Beacon is an early-stage monorepo. The repository contains planned workspaces for the web app, API, contracts, shared packages, docs, and scripts.

The backend workspace at `apps/api/` has a local Python virtual environment, installed backend dependencies, a Django project named `beacon_api`, and PostgreSQL configured through Docker Compose.

The frontend workspace at `apps/web/` has been initialized as a Nuxt app and currently keeps its pnpm package management inside `apps/web/`.

The current frontend includes a Beacon-branded, i18n-backed landing page with signup and login calls to action. Signup and login pages submit email-only account requests to the Django API.

## Changes Made

### 2026-06-02

* Created the initial monorepo directory structure with placeholder README, LICENSE, and documentation files.
* Added licensing placeholders:
  * AGPL v3 placeholder for the root repository, web app, and API app.
  * Apache 2.0 placeholder for contracts and SDK.
* Installed backend Python dependencies inside `apps/api/.venv/`:
  * Django 5.2.14
  * Django REST Framework 3.17.1
* Added `apps/api/requirements.txt` to track backend Python dependencies.
* Updated `apps/api/README.md` with beginner-friendly local setup and verification instructions.
* Added this handoff document at `docs/development/assistant-handoff.md`.
* Installed frontend staged-file tooling in `apps/web/`:
  * Husky 9.1.7
  * lint-staged 17.0.7
  * Prettier 3.8.3
* Installed backend development tooling in `apps/api/.venv/`:
  * Ruff 0.15.15
* Added `apps/api/requirements-dev.txt` for backend development dependencies.
* Added `apps/api/pyproject.toml` with Ruff lint/format configuration.
* Added frontend Prettier configuration in `apps/web/.prettierrc.json` and `apps/web/.prettierignore`.
* Added a tracked root pre-commit hook at `.husky/pre-commit`.
* Linked `.git/hooks/pre-commit` to `.husky/pre-commit` in this working copy.
* Added `docs/development/git-hooks.md` with hook behavior and setup instructions.
* Installed frontend E2E testing in `apps/web/`:
  * @playwright/test 1.60.0
  * Chromium browser installed through Playwright
* Added `apps/web/playwright.config.ts` and `apps/web/tests/e2e/smoke.spec.ts`.
* Installed backend testing tools in `apps/api/.venv/`:
  * pytest 9.0.3
  * pytest-django 4.12.0
  * factory-boy 3.3.3
* Added backend pytest configuration to `apps/api/pyproject.toml`.
* Added `apps/api/tests/test_smoke.py`.
* Added `docs/development/testing.md` with frontend and backend test commands.
* Initialized the Django project in `apps/api/` as `beacon_api`.
* Installed PostgreSQL/environment dependencies:
  * django-environ 0.13.0
  * psycopg 3.3.4
* Added environment-based Django settings using `apps/api/.env`.
* Added `apps/api/.env.example` for local backend configuration.
* Added `apps/api/compose.yaml` for a local PostgreSQL 16 database service.
* Created local ignored `apps/api/.env` from `.env.example` for this working copy.
* Added `docs/development/database.md` with database setup and migration commands.
* Django settings checks and backend smoke tests pass.
* Database migration verification is pending because the Docker daemon was not running during setup.
* Replaced the Nuxt starter landing page with a Beacon-specific landing page at `apps/web/app/pages/index.vue`.
* Replaced the starter logo with a Beacon wordmark in `apps/web/app/components/AppLogo.vue`.
* Updated the app shell metadata and navigation in `apps/web/app/app.vue`.
* Added auth routes, later connected to the email-only backend API:
  * `apps/web/app/pages/signup.vue`
  * `apps/web/app/pages/login.vue`
* Updated the frontend Playwright smoke test to assert Beacon landing content and auth links.
* Installed Nuxt i18n in `apps/web/`:
  * @nuxtjs/i18n 10.4.0
* Configured English and Persian locales in `apps/web/nuxt.config.ts`.
* Added locale messages:
  * `apps/web/i18n/locales/en.json`
  * `apps/web/i18n/locales/fa.json`
* Moved homepage, app shell, and auth placeholder copy to translation keys.
* Added `apps/web/app/components/LanguageSwitcher.vue`.
* Updated the frontend Playwright smoke test to check English and Persian landing pages.

## Decisions

* Backend dependencies are isolated inside `apps/api/.venv/` instead of the repository root.
* `apps/api/requirements.txt` is the current dependency tracking mechanism for the API workspace.
* Django and Django REST Framework are installed, and the Django project is initialized as `beacon_api`.
* Frontend package management remains app-local in `apps/web/` for now.
* Frontend user-facing copy should use Nuxt i18n messages instead of hardcoded strings.
* Git hooks live at the repository root, but delegate to app-local tooling.
* Tests are not run from pre-commit hooks. They should be run manually and later in CI.
* Docker Compose can now run both the local Django API service and PostgreSQL database.
* CI runs from the repository root and covers frontend lint/typecheck/E2E plus backend Ruff and pytest checks.
* No Turborepo, Anchor, or recommendation-domain Django application code has been generated yet.

## Next Steps

* Choose the initial API domain model for the MVP, likely centered on books, recommendations, stakes, and users.
* Create the first Django app after deciding the initial MVP domain model.
* Consider moving JavaScript package management to the repository root later when shared JS packages become active.
* Add build checks to CI when deployment targets are selected.
* Add recommendation-domain Django tests after domain apps are created.
* Expand frontend E2E coverage as real user flows are implemented.
* Replace email-only signup/login with wallet or password authentication when authentication is designed.
* Review Persian marketing copy with a native/product reviewer before launch.

## Useful Commands

Run backend commands from `apps/api/`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m django --version
cp .env.example .env
docker compose up -d postgres
.venv/bin/python manage.py migrate
docker compose up --build
docker compose run --rm api python manage.py migrate
docker compose run --rm api pytest
```

Run frontend commands from `apps/web/`.

```bash
pnpm install
pnpm lint-staged
pnpm lint
pnpm typecheck
pnpm exec playwright install chromium
pnpm test:e2e
```

Run backend tests from `apps/api/`.

```bash
.venv/bin/pytest
```

Enable the tracked pre-commit hook in a fresh clone from the repository root.

```bash
ln -s ../../.husky/pre-commit .git/hooks/pre-commit
```
