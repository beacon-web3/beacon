# Auth API Test Split

Status: Draft

## Context

`apps/api/tests/test_auth_api.py` has grown to more than 1,200 lines and mixes
signup, login, CSRF/session, password reset, email verification, throttling,
admin/model uniqueness, and localization coverage. The file still provides useful
regression coverage, but its size makes focused auth changes harder to review and
increases the risk of unrelated merge conflicts.

Relevant docs and plans:

- `docs/development/testing.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0006-email-verification-otp.md`
- `docs/plans/0007-backend-auth-hardening.md`
- `docs/plans/0008-auth-error-handling.md`
- `docs/plans/0009-backend-localization.md`

## Decisions

- Treat this as a behavior-preserving test refactor; do not change auth API
  behavior or production code as part of the split.
- Prefer a directory split under `apps/api/tests/auth/` so auth API test modules
  can share local fixtures without growing the global test namespace.
- Move admin/model uniqueness tests out of API auth modules when practical, since
  they validate model/admin behavior rather than request/response behavior.
- Keep existing test names where possible to preserve grepability and reduce
  review noise.

## Proposed File Layout

- `apps/api/tests/auth/conftest.py` for auth API fixtures such as `api_client`,
  `clear_rate_limit_cache`, shared passwords, and OTP helpers when local fixture
  scope is sufficient.
- `apps/api/tests/auth/test_signup.py`
- `apps/api/tests/auth/test_login.py`
- `apps/api/tests/auth/test_password_reset.py`
- `apps/api/tests/auth/test_email_verification.py`
- `apps/api/tests/auth/test_sessions_csrf.py`
- `apps/api/tests/auth/test_localization.py`
- `apps/api/tests/accounts/test_models.py` or another non-API location for
  account model uniqueness coverage.
- `apps/api/tests/accounts/test_admin.py` or another non-API location for
  `AccountAdmin` coverage.

## Tasks

- [ ] Create auth test package and shared fixtures.
  - Move shared constants, `api_client`, rate-limit cache cleanup, and OTP helpers
    into `apps/api/tests/auth/conftest.py` or an existing shared `conftest.py` if
    broader fixture scope is necessary.
  - Acceptance: The existing auth test file can import or resolve the shared
    helpers without behavior changes during the transition.
  - Verify: Run the current auth test file after fixture extraction.

- [ ] Split signup and login tests.
  - Move signup request/validation/email-scheduling tests to
    `apps/api/tests/auth/test_signup.py`.
  - Move login credential, verification-gating, and login response tests to
    `apps/api/tests/auth/test_login.py`.
  - Acceptance: Signup and login tests remain behavior-equivalent and retain the
    same request payloads, status-code assertions, and response-shape assertions.
  - Verify: Run the new signup and login test modules.

- [ ] Split password reset and email verification tests.
  - Move password reset request and confirmation tests to
    `apps/api/tests/auth/test_password_reset.py`.
  - Move email verification request and confirmation tests to
    `apps/api/tests/auth/test_email_verification.py`.
  - Acceptance: Generic account-enumeration responses, email outbox assertions,
    token/OTP edge cases, and attempt-limit assertions remain covered.
  - Verify: Run the new password reset and email verification test modules.

- [ ] Split sessions, CSRF, throttling, and localization tests.
  - Move browser-session and CSRF behavior to
    `apps/api/tests/auth/test_sessions_csrf.py`.
  - Move language negotiation and translated auth-response tests to
    `apps/api/tests/auth/test_localization.py`.
  - Keep throttling tests with the endpoint area they primarily validate unless a
    separate throttle module is clearer after the first split.
  - Acceptance: Localization tests cover representative English/French responses,
    including password-complexity validation, and session/CSRF tests remain
    endpoint-focused.
  - Verify: Run the new sessions/CSRF and localization test modules.

- [ ] Move model and admin uniqueness tests out of API auth coverage.
  - Move database uniqueness tests to an account model test module.
  - Move `AccountAdmin` tests to an admin test module.
  - Acceptance: API auth test modules only cover API behavior; model/admin tests
    remain covered in their own modules.
  - Verify: Run the new account model/admin test modules.

- [ ] Remove the monolithic auth API test file after all tests are relocated.
  - Delete `apps/api/tests/test_auth_api.py` only after every test has a new home.
  - Acceptance: No duplicate tests remain, no skipped tests are introduced, and
    pytest still discovers all relocated tests.
  - Verify: Run the backend auth/account test subset, then the full backend test
    suite if practical.

## Acceptance Criteria

- Auth API tests are split into focused modules with no intentional behavior
  changes.
- Shared fixtures are local to auth tests unless broader scope is demonstrably
  needed.
- Admin and model uniqueness tests no longer live in API auth test modules.
- Test names remain stable where practical.
- The split does not reduce coverage for signup, login, password reset, email
  verification, sessions/CSRF, throttling, localization, model uniqueness, or
  admin behavior.

## Verification

- `cd apps/api && ./scripts/test-postgres.sh tests/auth`
- `cd apps/api && ./scripts/test-postgres.sh tests/accounts`
- `cd apps/api && ./scripts/test-postgres.sh`
- `cd apps/api && ./.venv/bin/python -m ruff check .`

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Fixture extraction changes test isolation | Medium | Keep the autouse cache-clear fixture and verify endpoint groups independently before deleting the original file. |
| Tests are accidentally duplicated or dropped | High | Move one domain at a time and compare collected test counts before and after each phase. |
| Throttling tests become harder to place | Low | Keep throttling tests with the endpoint they validate unless a dedicated throttle module becomes clearer during the split. |
| Large refactor obscures localization fixes | Medium | Land this as a separate refactor from localization behavior changes. |

## Open Questions

- Should throttling tests live with endpoint modules or in a dedicated
  `test_throttling.py` module after the first split?
