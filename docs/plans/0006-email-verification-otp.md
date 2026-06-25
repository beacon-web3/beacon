# Email Verification OTP

Status: In Progress

## Context

Beacon has password-based Django session auth, but the Nuxt auth flow now routes
new users to an email verification page. The backend does not yet have an email
verification contract, so the backend API must be added before the frontend form
can submit real OTP values.

Relevant specs:

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/architecture/system-design.md`
- `docs/api/openapi.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`

## Decisions

- Gate login on verified email addresses.
- Use a six-digit numeric OTP sent by email for account verification.
- Store only a hashed OTP on the account record.
- Keep verification-request responses generic so account existence is not
  disclosed.
- Return a machine-readable `EMAIL_VERIFICATION_REQUIRED` error code on login
  when credentials are valid but the account email is unverified.
- Use Nuxt UI's segmented `UPinInput` for the frontend OTP field while preserving
  the backend `{ email, otp }` string contract.
- Enforce a configurable per-code verification attempt limit so a code must be
  replaced after too many failed confirmation attempts.

## Tasks

- [x] Add failing backend tests for signup OTP email, verification request,
  verification confirm, invalid OTP, expired OTP, and login gating.
- [x] Add account email verification fields and migration.
- [x] Add backend OTP generation, hashing, request, and confirmation logic.
- [x] Add backend tests for malformed OTPs, resend invalidation, verified-account
  resend behavior, and the configurable attempt limit.
- [x] Update auth API docs and changelog.
- [x] Add the Nuxt email verification form with email prefill, segmented OTP
  entry, and resend action.
- [x] Wire signup and unverified-login flows to the verification page.
- [x] Run targeted backend and frontend verification.

## Acceptance Criteria

- Signup creates an unverified account and sends a verification OTP email.
- Unverified accounts cannot log in even with valid credentials.
- Login for unverified accounts returns an `EMAIL_VERIFICATION_REQUIRED` code and
  the normalized email.
- Verification request returns `202 Accepted` with a generic response for both
  missing and existing accounts.
- Verification confirmation rejects malformed, invalid, expired, or over-attempt
  OTPs.
- Verification confirmation marks the account email as verified and allows login.
- The Nuxt verification page renders email and segmented OTP fields, prefills
  email from the query string, submits a six-digit OTP string to the backend, and
  can request another code.

## Verification

- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-email-verification-green.sqlite3" .venv/bin/pytest tests/test_auth_api.py` - passed, 32 tests.
- `cd apps/api && .venv/bin/ruff check .` - passed.
- `cd apps/web && pnpm typecheck` - passed.
- `cd apps/web && pnpm lint` - passed.
- `cd apps/web && pnpm test:e2e` - passed, 11 tests.
- `cd apps/web && CI=1 pnpm test:e2e tests/e2e/auth.spec.ts` - passed, 9 tests.

## Open Questions

- Production IP/user throttles, cooldowns, and monitoring for OTP request volume
  and failed confirmation attempts should be finalized before public launch.
