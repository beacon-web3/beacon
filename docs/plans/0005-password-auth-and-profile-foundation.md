# Password Auth and Profile Foundation

Status: Completed

## Context

Beacon's first auth slice accepted email-only signup and login. The next slice
adds conventional account credentials and profile identity fields while keeping
Beacon framed as a discovery and reputation network.

Relevant specs:

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/architecture/system-design.md`
- `docs/tokenomics/rewards.md`
- `docs/api/openapi.md`

## Decisions

- Use Django session cookies for browser authentication.
- Let users log in with either email or username plus password.
- Collect email, username, display name, and password at signup.
- Add nullable `wallet_address` directly to the user model for the MVP.
- Add reserved `reputation_score` and `account_credit` fields without economic
  formulas, withdrawal behavior, or tokenomics semantics.
- Use reCAPTCHA v2 Invisible for signup, login, and password reset requests.
- Keep future Google login as an identity-provider link to the same account,
  not a separate Beacon profile type.

## Tasks

- [x] Update API, testing, decision, and changelog documentation.
- [x] Replace email-only account persistence with a Django auth-compatible
  account model.
- [x] Add signup, login, logout, current-account, password-reset request, and
  password-reset confirmation endpoints.
- [x] Verify passwords through Django password hashing and validators.
- [x] Verify reCAPTCHA tokens server-side when captcha is enabled.
- [x] Update Nuxt auth forms for signup, login, and password reset flows.
- [x] Update backend and frontend tests for the new auth contract.
- [x] Run targeted backend and frontend verification.

## Acceptance Criteria

- Signup creates an authenticated account with normalized email, unique username,
  hashed password, display name, and reserved profile fields.
- Login accepts email-or-username plus password and establishes a Django session.
- Logout clears the session.
- Current-account endpoint returns the authenticated user's public account
  envelope and rejects anonymous requests.
- Password reset request always returns a generic accepted response and does not
  disclose whether an email exists.
- Password reset confirmation validates Django's token and sets a new password.
- Captcha failure prevents auth mutations when captcha is enabled.
- Frontend forms submit the documented payloads and surface accessible success
  and error states.

## Verification

- `cd apps/api && .venv/bin/pytest`
- `cd apps/web && pnpm test:e2e`
- `cd apps/web && pnpm typecheck`

Completed verification:

- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-auth-test.sqlite3" .venv/bin/pytest tests/test_auth_api.py`
- `cd apps/api && DATABASE_URL="sqlite:////var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-check.sqlite3" .venv/bin/python manage.py check`
- `cd apps/api && .venv/bin/ruff check .`
- `cd apps/web && pnpm typecheck`
- `cd apps/web && pnpm test:e2e`

Note: full backend pytest still requires the local PostgreSQL service. A full
SQLite run passed the auth tests and failed only the existing smoke assertion
that the configured database engine is PostgreSQL.

## Open Questions

- Exact reputation and account-credit semantics remain out of scope and must be
  resolved through the product/tokenomics specs before use.
