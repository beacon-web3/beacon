# Backend Auth Hardening

Status: Complete

## Context

A backend review found auth edge cases, abuse risks, stale documentation, and
missing regression tests around the Django session auth foundation and email OTP
verification flow.

Relevant specs and docs:

- `docs/api/openapi.md`
- `docs/architecture/system-design.md`
- `docs/decisions/0007-password-session-auth-foundation.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0006-email-verification-otp.md`

## Decisions

- Keep Django session auth and the existing REST contract.
- Validate captcha before account-existence checks on signup so captcha-enabled
  deployments do not leak duplicate account signals before bot screening.
- Add database-level case-insensitive uniqueness for email and username while
  preserving the existing normalized API behavior.
- Use Django's cache-backed throttle primitives for auth abuse controls without
  adding a new dependency.
- Keep local development defaults permissive, but make production cookie and SSL
  hardening configurable through environment variables.

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

## Acceptance Criteria

- Captcha-enabled duplicate signup attempts fail on captcha before revealing
  duplicate email or username validation errors.
- Account email and username uniqueness are enforced case-insensitively at the
  database boundary.
- Concurrent duplicate signup attempts return controlled validation errors.
- Signup rejects blank or whitespace-only display names.
- Signup email delivery failure leaves no newly created account behind.
- Auth abuse controls reject excess request volume with HTTP 429.
- CSRF enforcement remains active for authenticated unsafe session requests.
- Production deployments can opt into secure cookies, SSL redirect, HSTS, and
  explicit default email sender settings through environment variables.
- Public docs match the implemented auth API contract and configuration surface.

## Verification

- `cd apps/api && .venv/bin/pytest tests/test_auth_api.py` - blocked because
  local PostgreSQL was not running on `localhost:5432`.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/pytest tests/test_auth_api.py` - passed, 41 tests.
- `cd apps/api && .venv/bin/pytest tests/test_smoke.py` - passed, 5 tests.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/python manage.py check` - passed.
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-api-check.sqlite3" .venv/bin/python manage.py makemigrations --check --dry-run` - passed, no changes detected.
- `cd apps/api && .venv/bin/ruff check .` - passed.

## Open Questions

- Production throttle rates may need tuning after real traffic and abuse metrics
  exist; current values should start conservative and be configurable.
