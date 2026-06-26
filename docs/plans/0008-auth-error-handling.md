# Auth Error Handling Improvements

Status: Completed

## Context

Auth error handling should preserve account-enumeration protections while giving
users safe, actionable feedback for validation failures, throttling, and
recoverable client-side failures.

Relevant specs and docs:

- `docs/api/openapi.md`
- `docs/architecture/system-design.md`
- `docs/decisions/0007-password-session-auth-foundation.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0006-email-verification-otp.md`
- `docs/plans/0007-backend-auth-hardening.md`

## Decisions

- Preserve generic `202 Accepted` responses for password reset requests and
  email verification resend requests, including when email delivery fails.
- Surface safe frontend validation details that are already exposed by the API,
  such as duplicate signup fields, invalid OTP, invalid reset token, and
  password complexity failures.
- Treat HTTP 429 as a distinct user-facing retry-later condition.
- Log backend captcha verification transport or parsing failures without logging
  tokens or user secrets.
- Keep the frontend reCAPTCHA integration lightweight and retryable; do not add a
  new dependency for script loading.

## Tasks

- [x] Add backend regression tests for password reset request and email
  verification resend when email delivery raises.
- [x] Make password reset and email verification resend delivery best-effort with
  server-side exception logging and unchanged generic responses.
- [x] Add backend logging for reCAPTCHA verification transport and parse failures.
- [x] Add frontend E2E coverage for safe validation details, throttling, invalid
  OTP/reset-token responses, and network failures.
- [x] Add frontend API error interpretation for safe DRF error payloads, 429s,
  network failures, and `EMAIL_VERIFICATION_REQUIRED`.
- [x] Reset failed reCAPTCHA script loads and ensure widget containers are cleaned
  up when render or execute fails synchronously.
- [x] Update changelog and mark this plan complete after verification.

## Acceptance Criteria

- Existing-account password reset requests return the same generic `202` response
  when SMTP delivery fails as they do when delivery succeeds.
- Existing unverified-account email verification resend requests return the same
  generic `202` response when SMTP delivery fails as they do when delivery
  succeeds.
- Backend logs email delivery and reCAPTCHA transport/parse failures without
  exposing OTPs, reset tokens, captcha tokens, or raw request bodies.
- Frontend auth forms show safe backend validation messages for signup,
  verification confirmation, and password reset confirmation.
- Frontend auth forms show a retry-later message for 429 responses and a network
  message for request failures without an HTTP status.
- reCAPTCHA script load failure can be retried without reloading the page, and
  hidden widget containers are removed on synchronous render/execute failures.

## Verification

- [x] `cd apps/api && ./.venv/bin/python -m pytest tests/test_auth_api.py -k "email_delivery_fails or captcha_logs"` - 4 passed, 55 deselected.
- [x] `cd apps/api && ./.venv/bin/python -m pytest` - 64 passed.
- [x] `cd apps/api && ./.venv/bin/python -m ruff check .` - passed.
- [x] `cd apps/web && pnpm test:e2e tests/e2e/auth.spec.ts` - 16 passed.
- [x] `cd apps/web && pnpm lint` - passed.
- [x] `cd apps/web && pnpm typecheck` - passed.

## Open Questions

- None. Throttle copy can remain generic until production abuse metrics justify
  endpoint-specific retry guidance.
