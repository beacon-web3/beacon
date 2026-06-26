# Auth Test Split

Status: Completed

## Context

`apps/api/tests/test_auth_api.py` had grown to more than 1,200 lines and mixed
signup, login, CSRF/session, password reset, email verification, throttling,
admin/model uniqueness, settings, permissions, captcha, and localization
coverage. `apps/web/tests/e2e/auth.spec.ts` had grown to more than 500 lines and
mixed signup, login, email verification, password reset, API error handling,
CSRF, locale, and reCAPTCHA transport assertions.

Both files still provided useful regression coverage, but their size made
focused auth changes harder to review and increased the risk of unrelated merge
conflicts.

Relevant docs and plans:

- `docs/development/testing.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0006-email-verification-otp.md`
- `docs/plans/0007-backend-auth-hardening.md`
- `docs/plans/0008-auth-error-handling.md`
- `docs/plans/0009-backend-localization.md`

## Decisions

- Treat this as a behavior-preserving test refactor; do not change auth API,
  frontend auth UI, or production behavior as part of the split.
- Prefer focused backend modules under `apps/api/tests/auth/` for API auth
  coverage and separate `apps/api/tests/accounts/` modules for account model and
  admin coverage.
- Keep backend settings coverage in `apps/api/tests/test_settings.py` because it
  validates project configuration rather than endpoint behavior.
- Prefer focused frontend Playwright specs under `apps/web/tests/e2e/auth/` with
  local helpers for shared CSRF and reCAPTCHA setup.
- Keep existing test names where possible to preserve grepability and reduce
  review noise.

## Completed File Layout

Backend:

- `apps/api/tests/auth/conftest.py`
- `apps/api/tests/auth/helpers.py`
- `apps/api/tests/auth/test_signup.py`
- `apps/api/tests/auth/test_login.py`
- `apps/api/tests/auth/test_password_reset.py`
- `apps/api/tests/auth/test_email_verification.py`
- `apps/api/tests/auth/test_sessions_csrf.py`
- `apps/api/tests/auth/test_localization.py`
- `apps/api/tests/auth/test_captcha.py`
- `apps/api/tests/auth/test_throttling.py`
- `apps/api/tests/auth/test_permissions.py`
- `apps/api/tests/accounts/test_models.py`
- `apps/api/tests/accounts/test_admin.py`
- `apps/api/tests/test_settings.py`

Frontend:

- `apps/web/tests/e2e/auth/helpers.ts`
- `apps/web/tests/e2e/auth/signup.spec.ts`
- `apps/web/tests/e2e/auth/login.spec.ts`
- `apps/web/tests/e2e/auth/email-verification.spec.ts`
- `apps/web/tests/e2e/auth/password-reset.spec.ts`

Removed monolithic files:

- `apps/api/tests/test_auth_api.py`
- `apps/web/tests/e2e/auth.spec.ts`

## Tasks

- [x] Create backend auth test package and shared fixtures.
  - Moved shared auth test constants, API client fixture, cache cleanup, and OTP
    helpers into auth-local test support modules.
  - Acceptance: Relocated backend auth tests resolve shared helpers without
    behavior changes.
  - Verified by backend auth/account/settings collection and test runs.

- [x] Split backend signup and login tests.
  - Moved signup request, validation, duplicate, email-scheduling, and failure
    handling tests to `apps/api/tests/auth/test_signup.py`.
  - Moved login credential, verification-gating, and login response tests to
    `apps/api/tests/auth/test_login.py`.
  - Acceptance: Signup and login tests retain the same request payloads,
    status-code assertions, and response-shape assertions.

- [x] Split backend password reset and email verification tests.
  - Moved password reset request and confirmation tests to
    `apps/api/tests/auth/test_password_reset.py`.
  - Moved email verification request and confirmation tests to
    `apps/api/tests/auth/test_email_verification.py`.
  - Acceptance: Generic account-enumeration responses, email outbox assertions,
    token/OTP edge cases, stale serializer behavior, and attempt-limit assertions
    remain covered.

- [x] Split backend sessions, CSRF, throttling, captcha, permissions, and
      localization tests.
  - Moved browser-session and CSRF behavior to
    `apps/api/tests/auth/test_sessions_csrf.py`.
  - Moved language negotiation and translated auth-response tests to
    `apps/api/tests/auth/test_localization.py`.
  - Moved captcha handling to `apps/api/tests/auth/test_captcha.py`.
  - Moved throttle behavior to `apps/api/tests/auth/test_throttling.py`.
  - Moved public auth view permission coverage to
    `apps/api/tests/auth/test_permissions.py`.
  - Acceptance: Endpoint-level auth behavior remains covered in focused modules.

- [x] Move backend model, admin, and settings coverage out of API auth modules.
  - Moved database uniqueness tests to `apps/api/tests/accounts/test_models.py`.
  - Moved `AccountAdmin` tests to `apps/api/tests/accounts/test_admin.py`.
  - Moved DRF default permission and production security settings tests to
    `apps/api/tests/test_settings.py`.
  - Acceptance: API auth modules only cover API behavior; model, admin, and
    settings tests remain covered in their own modules.

- [x] Split frontend signup and login E2E tests.
  - Moved signup flow, locale forwarding, validation details, reCAPTCHA cleanup,
    password policy, password visibility, and confirmation mismatch coverage to
    `apps/web/tests/e2e/auth/signup.spec.ts`.
  - Moved login request, throttling, and unsafe error-detail handling coverage to
    `apps/web/tests/e2e/auth/login.spec.ts`.
  - Acceptance: Frontend signup/login E2E coverage remains behavior-equivalent
    and keeps stable user-facing selectors.

- [x] Split frontend email verification and password reset E2E tests.
  - Moved email verification confirmation, resend, and invalid OTP detail coverage
    to `apps/web/tests/e2e/auth/email-verification.spec.ts`.
  - Moved password reset request, confirmation, invalid token, network failure,
    and weak-password coverage to `apps/web/tests/e2e/auth/password-reset.spec.ts`.
  - Acceptance: Frontend request payload, CSRF header, reCAPTCHA token, and
    user-visible response assertions remain covered.

- [x] Remove monolithic auth test files after all tests are relocated.
  - Deleted `apps/api/tests/test_auth_api.py` and
    `apps/web/tests/e2e/auth.spec.ts`.
  - Acceptance: No duplicate tests remain, no skipped tests are introduced, and
    the relocated test subsets are still discovered.

## Acceptance Criteria

- Auth API tests are split into focused modules with no intentional behavior
  changes.
- Frontend auth E2E tests are split into focused modules with no intentional
  behavior changes.
- Shared fixtures/helpers are local to auth tests unless broader scope is needed.
- Admin, model uniqueness, and settings tests no longer live in API auth modules.
- Test names remain stable where practical.
- The split does not reduce coverage for signup, login, password reset, email
  verification, sessions/CSRF, throttling, captcha, localization, permissions,
  settings, model uniqueness, or admin behavior.

## Verification

Completed:

- `cd apps/api && ./scripts/test-postgres.sh tests/test_auth_api.py --collect-only -q`
  collected 65 baseline backend tests before the split.
- `cd apps/api && ./scripts/test-postgres.sh tests/auth tests/accounts tests/test_settings.py --collect-only -q`
  collected 65 relocated backend tests after the split.
- `cd apps/api && ./scripts/test-postgres.sh tests/auth tests/accounts tests/test_settings.py`
  passed 65 relocated backend tests.
- `cd apps/web && pnpm exec playwright test --list` discovered 19 relocated auth
  E2E tests and 3 existing smoke tests.
- `cd apps/web && pnpm exec playwright test tests/e2e/auth --reporter=list`
  passed 19 relocated frontend auth E2E tests.

Recommended broader checks before merge if time permits:

- `cd apps/api && ./scripts/test-postgres.sh`
- `cd apps/api && ./.venv/bin/python -m ruff check .`
- `cd apps/web && pnpm test:e2e`
- `cd apps/web && pnpm lint`

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Fixture extraction changes test isolation | Medium | Keep auth helpers local and verify endpoint groups independently before deleting monolithic files. |
| Tests are accidentally duplicated or dropped | High | Compare collected backend test counts before and after the split, and use Playwright list output for frontend discovery. |
| Frontend shared helper becomes a hidden global fixture | Low | Keep CSRF and reCAPTCHA setup explicit through `prepareAuthPage` in each auth spec. |
| Large refactor obscures behavior changes | Medium | Keep this as a test-only refactor from auth behavior changes. |

## Open Questions

- None.
