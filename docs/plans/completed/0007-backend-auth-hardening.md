# Backend Auth Hardening

## Status

Completed

## Context

A backend review found auth edge cases, abuse risks, stale documentation, and
missing regression tests around the Django session auth foundation and email OTP
verification flow.

Relevant specs and docs:

- `docs/api/openapi.md`
- `docs/architecture/system-design.md`
- `docs/decisions/0007-password-session-auth-foundation.md`
- `docs/plans/completed/0005-password-auth-and-profile-foundation.md`
- `docs/plans/completed/0006-email-verification-otp.md`

## Decisions

- Keep Django session auth and the existing REST contract.
- Validate captcha before account-existence checks on signup so captcha-enabled
  deployments do not leak duplicate account signals before bot screening.
- Add database-level case-insensitive uniqueness for email and username while
  preserving the existing normalized API behavior.
- Use Django's cache-backed throttle primitives for auth abuse controls.
- Keep local development defaults permissive, but make production cookie and SSL
  hardening configurable through environment variables.
- Signup returns `201 Created` after the account transaction commits even if the
  post-commit verification email send fails; users can request another
  verification code through the resend endpoint.

## Tasks

- [x] Add regression tests for captcha-before-duplicate-signals, whitespace
  display names, duplicate username handling, case-insensitive database
  uniqueness, concurrent duplicate signup errors, request throttling, email send
  failure behavior, CSRF enforcement, and production security settings.
- [x] Harden account validation and persistence for captcha ordering,
  display-name trimming, duplicate race handling, and case-insensitive database
  uniqueness.
- [x] Add auth request throttles for signup, login, password reset request,
  email verification request, and email verification confirmation.
- [x] Add configurable production security settings for secure cookies, SSL
  redirect, HSTS, and email delivery metadata.
- [x] Update API docs, README, environment example, testing docs, related plan
  status, and changelog entries.
- [x] Run backend tests, Django checks, migration checks, and Ruff.

## Review Follow-Up Tasks

- [x] Change the global DRF permission default to authenticated access and make
  public auth endpoints explicitly opt into anonymous access.
- [x] Add throttling to password reset confirmation requests.
- [x] Move verification email delivery until after successful signup transaction
  commit.
- [x] Make email verification attempt increments concurrency-safe.
- [x] Ensure Django admin account creation includes required Beacon profile
  fields.
- [x] Resolve environment naming drift for the Django debug default.
- [x] Remove redundant case-sensitive email uniqueness. Keep Django's inherited
  username uniqueness because `username` remains the `USERNAME_FIELD` and Django
  requires it to be unique.
- [x] Replace custom local CORS middleware with a standard Django CORS package.
- [x] Add regression coverage for the auth hardening follow-up changes.
- [x] Make post-commit signup verification email delivery best-effort so SMTP
  failure does not turn a committed account creation into an HTTP 500.
- [x] Make successful email verification confirmation single-use under
  concurrent requests.
- [x] Add identifier-aware throttling for auth endpoints that validate reusable
  credentials or tokens.
- [x] Add settings import coverage for production auth/security environment
  parsing.
- [x] Document email delivery failure behavior for signup and reset/resend
  endpoints.
- [x] Add a production launch TODO to enable reCAPTCHA before public traffic.

## 2026-06-26 Review Follow-Up Tasks

- [x] Issue a usable CSRF token during browser session establishment and add a
  positive backend regression test for an authenticated unsafe request with the
  matching `X-CSRFToken` header.
- [x] Add a shared Nuxt backend API transport that sends `X-CSRFToken` for
  unsafe requests when the `csrftoken` cookie is present.
- [x] Execute frontend reCAPTCHA when `NUXT_PUBLIC_RECAPTCHA_SITE_KEY` is set
  and send tokens to captcha-protected public auth endpoints.
- [x] Reuse password complexity validation for password reset confirmation and
  add Playwright coverage for reset-confirm request shape and weak-password
  blocking.
- [x] Replace placeholder package, contracts, and scripts README TODOs with
  current implementation status and boundaries.
- [x] Update related auth docs and changelog entries after implementation.

## Acceptance Criteria

- Captcha-enabled duplicate signup attempts fail on captcha before revealing
  duplicate email or username validation errors.
- Account email and username uniqueness are enforced case-insensitively at the
  database boundary.
- Concurrent duplicate signup attempts return controlled validation errors.
- Signup rejects blank or whitespace-only display names.
- Signup verification email delivery is scheduled only after the signup
  transaction commits.
- Auth abuse controls reject excess request volume with HTTP 429.
- CSRF enforcement remains active for authenticated unsafe session requests.
- Production deployments can opt into secure cookies, SSL redirect, HSTS, and
  explicit default email sender settings through environment variables.
- Public docs match the implemented auth API contract and configuration surface.
- API endpoints are authenticated by default unless explicitly declared public.
- Password reset confirmation, verification code attempts, and signup email
  delivery remain abuse-resistant and transactionally safe.
- Django admin account creation supports required account profile fields.
- Signup still returns `201 Created` when account creation committed but the
  verification email send fails after commit.
- Production auth/security settings are covered by tests that exercise
  environment parsing at settings import time.
- Browser session-establishing auth responses provide a usable CSRF cookie, and
  Nuxt backend API requests send `X-CSRFToken` for unsafe methods when available.
- reCAPTCHA-enabled frontend auth submissions include fresh tokens without
  changing disabled/local-development behavior.
- Password reset confirmation enforces the same client-side password complexity
  requirements as signup.

## Verification

- `cd apps/api && .venv/bin/pytest tests/test_auth_api.py` - blocked because
  local PostgreSQL was not running on `localhost:5432`.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/pytest tests/test_auth_api.py` - passed, 41 tests.
- `cd apps/api && .venv/bin/pytest tests/test_smoke.py` - passed, 5 tests.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/python manage.py check` - passed.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/python manage.py makemigrations --check --dry-run` - passed, no changes detected.
- `cd apps/api && .venv/bin/ruff check .` - passed.
- `cd apps/api && ./.venv/bin/python -m pytest tests/test_auth_api.py` - passed,
  50 tests after installing updated dev requirements.
- `cd apps/api && ./.venv/bin/python -m ruff check .` - passed.
- `cd apps/api && ./.venv/bin/python -m pytest` - passed, 55 tests.
- `cd apps/api && ./.venv/bin/python manage.py check` - passed.
- `cd apps/api && ./.venv/bin/python manage.py makemigrations --check --dry-run`
  - passed, no changes detected.
- `cd apps/api && ./.venv/bin/python -m ruff check .` - passed.
- `cd apps/api && ./.venv/bin/python -m pytest tests/test_auth_api.py -k "post_commit_verification_email_fails or stale_success or keyed_by_identifier or parsed_from_environment"` - passed, 4 tests.
- `cd apps/api && ./.venv/bin/python -m pytest` - passed, 59 tests.
- `cd apps/api && ./.venv/bin/python manage.py check` - passed.
- `cd apps/api && ./.venv/bin/python manage.py makemigrations --check --dry-run`
  - passed, no changes detected.
- `cd apps/api && ./.venv/bin/python -m ruff check .` - passed.
- `cd apps/api && ./.venv/bin/python -m pytest tests/test_auth_api.py -k "csrf or logout or login_sets_csrf"` - passed, 3 tests.
- `cd apps/web && pnpm test:e2e tests/e2e/auth.spec.ts` - passed, 12 tests.
- `cd apps/web && pnpm lint` - passed.
- `cd apps/web && pnpm typecheck` - passed.
- `cd apps/api && ./.venv/bin/python -m ruff check .` - passed.

## Open Questions

- Production throttle rates may need tuning after real traffic and abuse metrics
  exist; current values should start conservative and be configurable.
- Enable reCAPTCHA for production/public launch once site keys and operational
  ownership are ready.
