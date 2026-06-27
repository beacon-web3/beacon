# Google Social Auth

Status: Implemented

## Context

Beacon currently supports email/password account signup, email verification,
session-cookie login, logout, current-account lookup, password reset, reCAPTCHA
for abuse-sensitive public auth mutations, and CSRF protection for browser
session requests.

This plan adds open social authentication starting with Google. GitHub and Apple
are expected later, but the first implementation should prove the shared social
auth contract with one provider before expanding the provider surface.

Relevant specs and docs:

- `docs/product/user-stories.md`
- `docs/product/mvp.md`
- `docs/architecture/system-design.md`
- `docs/api/openapi.md`
- `docs/development/testing.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0007-backend-auth-hardening.md`

## User Decisions

- Start with Google as the only social provider.
- Keep the implementation provider-aware so GitHub and Apple can be added later.
- Social signup is open.
- If a Google account has the same verified email as an existing password account,
  Beacon should auto-link the Google identity to that account and log the user in.
- If a Google login is attempted for a verified Google email with no Beacon
  account, Beacon should create an account and log the user in.
- Login and signup entry points should converge: if a user starts from signup and
  already has a matching Beacon account, Beacon should log them in instead of
  failing with a duplicate-account error.
- Beacon should generate a username for social-only users and let users edit it
  later.

## Provider Recommendation

- Implement Google first only.
- Defer GitHub until the Google flow, account linking rules, tests, and session
  behavior are stable. GitHub can hide primary emails or return multiple emails,
  so verified-email selection needs provider-specific handling.
- Defer Apple until after Google and GitHub. Apple requires extra operational
  setup around Services IDs, private-key based client secret generation, and
  private relay email behavior.
- Keep provider-specific normalization in a small backend adapter layer so future
  providers do not change Beacon's account/session contract.

## Decisions

- Preserve Django session-cookie authentication as the browser auth mechanism.
- Do not introduce JWTs or store auth tokens in localStorage.
- Use a mature Django OAuth/OIDC integration, preferably `django-allauth`, rather
  than hand-rolling OAuth state, token exchange, and provider account storage.
- Keep provider access tokens server-side and never return them to Nuxt.
- Do not store provider refresh tokens unless a future provider-backed API feature
  explicitly requires offline access.
- Treat Google email as verified only when Google's verified-email claim is true.
- Auto-link by email only when the provider email is verified.
- Generated usernames must be unique, stable, readable enough for early access,
  and editable later through a separate profile-editing feature.
- Social login is account authentication only; it is not wallet identity, proof of
  Solana account ownership, or an anti-sybil guarantee.

## Implemented API Contract

The final contract is documented in `docs/api/openapi.md`.

- `GET /api/auth/social/providers/`
  - Returns enabled social providers, initially Google only.
  - Does not expose client secrets or provider tokens.

- `POST /api/auth/social/google/start/`
  - Starts Google OAuth/OIDC authorization.
  - Accepts an optional `next` path constrained to same-site relative paths.
  - Returns an authorization URL or a redirect response, depending on the final
    frontend integration choice.
  - Creates provider state using server-side session storage.

- `GET /api/auth/social/google/callback/`
  - Handles Google's redirect callback.
  - Validates state and provider response.
  - Creates, links, or logs into a Beacon account according to the user decisions
    above.
  - Calls Django `login()` and issues a usable CSRF cookie.
  - Redirects back to Nuxt with a success or generic error code only; no tokens.

- Future endpoint, separate plan unless needed now:
  - `POST /api/auth/social/google/disconnect/`

## Backend Tasks

- [x] Update product/API documentation for Google social auth.
  - Acceptance: User stories and API docs describe open Google social login,
    account creation, auto-linking, generated usernames, session behavior, and
    failure responses without introducing wallet identity claims.
  - Verify: Documentation review against this plan and existing auth docs.
  - Files likely touched: `docs/product/user-stories.md`, `docs/api/openapi.md`,
    `CHANGELOG.md`.

- [x] Add an ADR for the social auth strategy.
  - Acceptance: The ADR records why Beacon uses server-side Django social auth,
    session cookies, Google-first rollout, verified-email auto-linking, and no
    browser-exposed provider tokens.
  - Verify: `docs/decisions/README.md` includes the new ADR.
  - Files likely touched: `docs/decisions/*.md`, `docs/decisions/README.md`.

- [x] Add and configure the social auth dependency.
  - Acceptance: Django settings include the social auth apps, middleware/settings
    required by the chosen library, provider configuration from environment
    variables, and local-development defaults that do not require real secrets.
  - Verify: `cd apps/api && ./.venv/bin/python manage.py check`.
  - Files likely touched: `apps/api/requirements.txt`,
    `apps/api/beacon_api/settings.py`, `apps/api/.env.example`,
    `apps/api/README.md`.

- [x] Add Google provider URL routes and auth views.
  - Acceptance: Provider list, start, and callback endpoints exist under
    `/api/auth/social/google/`; anonymous access is explicit; existing protected
    API defaults remain authenticated.
  - Verify: Targeted backend tests for route availability and permission behavior.
  - Files likely touched: `apps/api/accounts/urls.py`,
    `apps/api/accounts/views.py`, `apps/api/tests/auth/test_social_auth.py`.

- [x] Implement account resolution and auto-linking rules.
  - Acceptance: A verified Google email matching an existing password account
    links to that account and logs in; a verified Google email without an account
    creates an account and logs in; unverified provider email cannot auto-link by
    email; duplicate/race cases produce controlled errors.
  - Verify: Backend tests cover existing account, new account, unverified email,
    duplicate social identity, and concurrent account creation/linking behavior.
  - Files likely touched: `apps/api/accounts/views.py`,
    `apps/api/accounts/serializers.py` or a new focused service module,
    `apps/api/tests/auth/test_social_auth.py`.

- [x] Generate usernames for social-created accounts.
  - Acceptance: Social-created accounts receive a unique username derived from
    safe provider data where possible, with a collision-resistant fallback; users
    can later edit usernames through a separate profile feature.
  - Verify: Backend tests cover normalization, collisions, reserved/invalid
    characters, and database uniqueness races.
  - Files likely touched: `apps/api/accounts/models.py` or a new account utility
    module, `apps/api/tests/accounts/`.

- [x] Preserve session and CSRF behavior.
  - Acceptance: Successful callback establishes a Django session, returns only
    safe redirect data to Nuxt, and issues a `csrftoken` cookie usable by the
    existing `useApiFetch` transport.
  - Verify: Backend tests confirm session authentication and CSRF cookie issuance;
    existing login/logout/me tests continue to pass.
  - Files likely touched: `apps/api/accounts/views.py`,
    `apps/api/tests/auth/test_social_auth.py`, existing auth tests if helpers are
    reused.

- [x] Add social auth abuse controls and security logging.
  - Acceptance: Start and callback endpoints are throttled; failures are logged
    without secrets or provider tokens; user-facing callback errors remain
    generic.
  - Verify: Backend tests cover throttle responses and generic failure shapes.
  - Files likely touched: `apps/api/accounts/throttles.py`,
    `apps/api/accounts/views.py`, `apps/api/beacon_api/settings.py`,
    `apps/api/tests/auth/test_social_auth.py`.

## Frontend Tasks

- [x] Add Google social auth controls to auth screens.
  - Acceptance: Login and signup pages show an accessible `Continue with Google`
    action while preserving email/password forms, password reset, reCAPTCHA copy,
    and localization.
  - Verify: `cd apps/web && pnpm typecheck`; Playwright auth tests confirm button
    rendering.
  - Files likely touched: `apps/web/app/components/auth/AuthForm.vue`,
    `apps/web/app/components/auth/AuthScreen.vue`, `apps/web/i18n/locales/en.json`,
    `apps/web/i18n/locales/fr.json`.

- [x] Implement social auth start and completion handling.
  - Acceptance: Clicking Google starts backend social auth; callback completion
    confirms session with `/api/auth/me/`; success and failure states are
    localized and accessible; no provider tokens are handled by Nuxt.
  - Verify: Playwright tests mock backend start/callback outcomes.
  - Files likely touched: `apps/web/app/pages/(auth)/login.vue`,
    `apps/web/app/pages/(auth)/signup.vue`, optional
    `apps/web/app/pages/(auth)/auth-callback.vue`, auth E2E tests.

## Future Provider Tasks

- [ ] Add GitHub provider support in a follow-up plan.
  - Acceptance: GitHub email selection uses only verified provider emails and
    handles private primary-email cases without unsafe auto-linking.
  - Verify: Provider-specific backend tests for verified and unavailable email
    behavior.

- [ ] Add Apple provider support in a follow-up plan.
  - Acceptance: Apple client-secret generation, key rotation, Services ID setup,
    and private relay email behavior are documented before implementation.
  - Verify: Provider-specific backend tests and deployment configuration review.

## Acceptance Criteria

- Google is the only enabled initial social provider.
- Social signup is open.
- Google login and Google signup converge to the same account resolution behavior.
- A verified Google email matching an existing password account auto-links and
  logs the user in.
- A verified Google email with no Beacon account creates a Beacon account and logs
  the user in.
- Social-created users receive a unique generated username.
- Social auth uses Django sessions and CSRF cookies, not browser-stored tokens.
- Provider tokens and secrets are never exposed to frontend code or logs.
- Existing email/password signup, login, logout, email verification, password
  reset, reCAPTCHA, throttling, and CSRF behavior continue to pass tests.
- Docs clearly state social auth is not wallet identity or proof of Solana
  ownership.

## Verification

Implementation verification status:

- `cd apps/api && ./.venv/bin/ruff check .` passed.
- `cd apps/api && ./.venv/bin/python manage.py check` passed.
- `cd apps/api && ./.venv/bin/python manage.py makemigrations --check --dry-run`
  reported `No changes detected`; database migration-history checking warned that
  local PostgreSQL was not reachable.
- `cd apps/api && ./scripts/test-postgres.sh tests/auth/test_social_auth.py` was
  blocked because Docker was not running or not reachable.
- `cd apps/web && pnpm lint` passed.
- `cd apps/web && pnpm typecheck` passed.
- `cd apps/web && pnpm test:e2e tests/e2e/auth/login.spec.ts tests/e2e/auth/signup.spec.ts`
  passed.

- `cd apps/api && ./scripts/test-postgres.sh tests/auth tests/accounts tests/test_settings.py`
- `cd apps/api && docker compose run --rm api ruff check .`
- `cd apps/api && docker compose run --rm api python manage.py check`
- `cd apps/api && docker compose run --rm api python manage.py makemigrations --check --dry-run`
- `cd apps/web && pnpm lint`
- `cd apps/web && pnpm typecheck`
- `cd apps/web && pnpm exec playwright test tests/e2e/auth`

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OAuth account takeover through unsafe email auto-linking | High | Auto-link only when Google explicitly reports the email as verified; never auto-link unverified provider emails. |
| Provider token leakage | High | Keep token exchange server-side; never return provider tokens to Nuxt; redact auth logs. |
| OAuth CSRF/state bypass | High | Use library-managed state validation and add callback rejection tests. |
| Username collisions for social-created accounts | Medium | Generate usernames through a uniqueness-checked helper with database-race handling. |
| Provider expansion causing auth contract drift | Medium | Keep Google-specific normalization isolated behind a provider adapter and preserve the same Beacon session contract. |
| Apple implementation complexity | Medium | Defer Apple to a follow-up plan with explicit operational setup and key-rotation documentation. |

## Questions & Answers

- What exact generated-username format should Beacon use for social-created
  accounts? Username format: normalized email local part plus random suffix.
- Should profile editing, including username changes, be implemented in the same
  delivery window or tracked as a separate plan? The profile edit feature should already be implemented. If it is not, create a separate follow-up task.
- What post-login destination should social auth use by default after callback? Redirect behavior: redirect to `/dashboard` which should be a protected path
- Should social auth starts require reCAPTCHA, or are throttling and provider
  abuse controls sufficient for the first Google rollout? Social auth abuse control: throttling and logging first, no reCAPTCHA initially.
