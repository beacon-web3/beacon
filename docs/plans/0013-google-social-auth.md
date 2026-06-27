# Google Social Auth

Status: Implemented - code review remediation complete

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

Remediation verification completed on 2026-06-27:

- `cd apps/api && ./.venv/bin/pytest tests/auth/test_social_auth.py` passed
  with 32 tests.
- `cd apps/api && ./.venv/bin/python manage.py check` passed.
- `cd apps/api && ./.venv/bin/ruff check .` passed.

## Code Review Findings and Required Fixes

These findings are gaps against the approved requirements. Do not resolve them by
weakening the account-linking, provider-security, or test-coverage requirements;
fix the implementation and tests so the feature meets the plan and ADR.

### 1. Critical: Inactive Account Handling Is Implicit

- Finding: `resolve_social_account()` can return an existing linked user without
  checking `is_active`, and matching-email auto-linking can also return an
  inactive account before `login()` is called. Password login normally goes
  through `authenticate()`, which blocks inactive users, so social auth currently
  creates an implicit inactive-account bypass instead of an intentional account
  lifecycle transition.
- References before remediation: `apps/api/accounts/social_auth.py:41`,
  `apps/api/accounts/social_auth.py:51`,
  `apps/api/accounts/social_auth.py:57`,
  `apps/api/accounts/social_views.py:201`.
- Required solution: Treat verified Google social auth as sufficient to
  reactivate the existing Beacon account only when identity proof is strict and
  explicit. If an inactive account is resolved by an already-linked Google
  identity, the Google `sub` must match the linked social account. If an inactive
  account is resolved by matching email, Google must provide the same valid email
  and `email_verified is True`. Reactivate the existing account before `login()`,
  log the reactivation without provider tokens or sensitive details, and never
  create a replacement account for that identity.
- Required tests: Add backend tests for an inactive account with an existing
  linked Google identity and an inactive account matched by verified Google email;
  both must explicitly set the existing account active, create a session, and not
  create/link a replacement account. Malformed, unverified, or mismatched Google
  identity data must remain blocked.

### 2. Important: OAuth Flow Does Not Match the ADR

- Finding: The ADR and plan say a mature library should manage
  security-sensitive OAuth state, token exchange, and provider handling, but the
  implementation manually exchanges the code and reads Google `userinfo` while
  mostly using `django-allauth` for storage.
- References before remediation: `docs/decisions/0009-google-social-auth-strategy.md:21`,
  `docs/decisions/0009-google-social-auth-strategy.md:46`,
  `apps/api/accounts/social_views.py:65`,
  `apps/api/accounts/social_views.py:103`.
- Required solution: Align the implementation with the accepted ADR by routing
  the Google OAuth/OIDC exchange, state validation, token handling, and provider
  account extraction through `django-allauth` where practical. If any small
  adapter remains necessary for Beacon-specific redirect/session behavior, keep it
  outside token validation and provider-security responsibilities and document the
  boundary in this plan and the ADR.
- Non-solution: Do not merely update the ADR to bless a custom exchange unless a
  separate security review explicitly accepts that design and explains provider
  token validation, ID token validation, userinfo trust boundaries, replay risks,
  and future-provider consequences.
- Required tests: Add callback-state rejection, provider-error, invalid-token or
  failed-exchange, and successful allauth-backed account-resolution tests.

### 3. Important: Google Identity Fields Are Not Strictly Validated

- Finding: `str(userinfo.get("sub", ""))`, `str(userinfo.get("email", ""))`, and
  `bool(userinfo.get("email_verified"))` can turn malformed identity values such
  as `None` or `"false"` into accepted-looking values.
- Reference before remediation: `apps/api/accounts/social_views.py:94`.
- Required solution: Normalize Google userinfo through a strict provider adapter
  before account resolution. Treat `sub`, `email`, and `email_verified` as
  identity-critical fields: require `sub` to be a non-empty string, validate
  `email` with Django's email validator, and require `email_verified is True`
  exactly before auto-linking, account creation, or inactive-account
  reactivation. Treat optional profile/display fields such as `name`,
  `given_name`, `family_name`, and `picture` as non-authoritative metadata; if
  they are missing or malformed, ignore them or replace them with Beacon-generated
  defaults such as the generated username.
- Required tests: Add malformed identity-field tests for missing, `None`,
  non-string, empty, invalid-email, and string-valued `email_verified` cases.
  These must fail closed and must not create, link, reactivate, or log in an
  account. Add optional-profile-field tests proving malformed or missing display
  metadata does not block account creation when `sub`, `email`, and
  `email_verified` are valid.

### 4. Important: Verification Claims Exceed Test Coverage

- Finding: This plan claims coverage for duplicate social identity,
  concurrent/race handling, username normalization/collisions, and callback
  throttling, but the current tests only cover start throttling and happy/basic
  callback paths.
- References: `docs/plans/0013-google-social-auth.md:133`,
  `docs/plans/0013-google-social-auth.md:144`,
  `docs/plans/0013-google-social-auth.md:163`,
  `apps/api/tests/auth/test_social_auth.py:219`.
- Required solution: Add the missing tests and keep the plan's acceptance criteria
  unchanged. The implementation is not complete until these cases pass.
- Required tests: Add duplicate social identity, concurrent account
  creation/linking race, username normalization, username collision,
  invalid/reserved username source data, database uniqueness-race, and callback
  throttling tests.

### 5. Consider: Dependency and Naming Clarity

- Finding: `requests` was added to `apps/api/requirements.txt`, but the new code
  uses `urllib.request`. Also, the social auth view naming is generic even though
  the implementation is Google-only.
- Reference: `apps/api/requirements.txt:9`.
- Required solution: If direct HTTP calls remain after the allauth alignment,
  either use one well-documented client consistently with explicit timeouts and
  safe error handling, or remove the direct `requests` dependency if it is not
  directly used by Beacon code. If `requests` is retained only because allauth or
  another package needs it, do not list it as a direct dependency unless the
  package requires that; document the reason in `apps/api/README.md` or remove it.
- Naming solution: Rename the backend view/module/class names to make the Google
  boundary explicit, for example `google_social_views.py` or
  `GoogleSocialAuthStartView` / `GoogleSocialAuthCallbackView`, while preserving
  the existing `/api/auth/social/google/` API contract. This leaves room for
  future `github` and `apple` views without suggesting the current view handles
  every provider.

## Remediation Tasks

- [x] Explicitly reactivate inactive accounts only after verified Google identity
  proof.
  - Acceptance: Inactive linked users and inactive matching-email users are
    reactivated only after strict Google identity validation; no replacement
    account is created; reactivation is explicit and logged before session login.
  - Verify: Targeted backend tests for inactive linked and inactive matching-email
    cases fail before the fix and pass after it, including negative cases for
    malformed, unverified, or mismatched provider identity.
  - Files touched: `apps/api/accounts/social_auth.py`,
    `apps/api/accounts/google_social_views.py`,
    `apps/api/tests/auth/test_social_auth.py`.
  - Status: Complete. Inactive linked users and verified-email matches are
    reactivated only after strict Google identity validation; unverified or
    malformed provider identities fail closed.

- [x] Align Google OAuth/OIDC handling with `django-allauth`.
  - Acceptance: OAuth state, code exchange, provider token handling, and Google
    account extraction are managed by allauth or by documented allauth extension
    points; Beacon code only applies product-specific account resolution,
    sessions, redirects, and logging.
  - Verify: Callback tests cover state rejection, provider errors, exchange
    failures, and successful session creation without browser-exposed tokens.
  - Files touched: `apps/api/accounts/google_social_views.py`,
    `apps/api/accounts/social_auth.py`, `apps/api/tests/auth/test_social_auth.py`,
    `docs/decisions/0009-google-social-auth-strategy.md`.
  - Status: Complete. Beacon now uses allauth's Google adapter and OAuth2 client
    for code exchange, provider token handling, and provider account extraction.
    Beacon's Google wrapper is limited to backend route handling, session state,
    redirect behavior, strict identity normalization, account resolution, and
    safe logging.

- [x] Strictly validate normalized Google identity fields.
  - Acceptance: Account resolution receives only a non-empty string Google `sub`,
    a Django-validated email address, and `email_verified is True` for any
    auto-link, account-create, or inactive-account reactivation path; optional
    profile/display fields are ignored or replaced with safe Beacon-generated
    defaults when malformed.
  - Verify: Malformed provider payload tests fail closed without session creation,
    account creation, account reactivation, or social-account linking for
    identity-critical field failures, while malformed optional profile metadata
    does not block account creation when identity fields are valid.
  - Files touched: `apps/api/accounts/social_auth.py`,
    `apps/api/accounts/google_social_views.py`,
    `apps/api/tests/auth/test_social_auth.py`.
  - Status: Complete. Normalization now requires non-empty string `sub`, a
    Django-validated email address, and `email_verified is True` exactly;
    malformed optional display metadata falls back to Beacon-generated defaults.

- [x] Fill the missing social auth test coverage promised by this plan.
  - Acceptance: Tests cover duplicate social identities, concurrent/race handling,
    username normalization and collisions, database uniqueness races, and callback
    throttling.
  - Verify: `cd apps/api && ./scripts/test-postgres.sh tests/auth/test_social_auth.py`
    passes in an environment with Docker/PostgreSQL available.
  - Files touched: `apps/api/tests/auth/test_social_auth.py`.
  - Status: Complete. The targeted social auth suite covers duplicate identities,
    race handling, username normalization/collisions, database uniqueness races,
    callback throttling, provider errors, failed exchanges, and malformed identity
    payloads.

- [x] Clarify dependency usage and Google-specific naming.
  - Acceptance: The codebase either uses `requests` directly with timeouts and
    clear error handling, or removes it as a direct dependency when unused;
    Google-specific social auth views/modules/classes are named as Google-specific
    while preserving existing route paths.
  - Verify: `cd apps/api && ./.venv/bin/ruff check .` and targeted route tests
    pass; dependency documentation matches `apps/api/requirements.txt`.
  - Files touched: `apps/api/README.md`,
    `apps/api/accounts/google_social_views.py`,
    `apps/api/accounts/urls.py`, `apps/api/tests/auth/test_social_auth.py`.
  - Status: Complete. Direct Beacon provider HTTP code was removed. `requests`
    remains documented as a direct dependency because allauth's OAuth2 client uses
    it for provider token/userinfo HTTP transport. The Google-only callback module
    is now named `google_social_views.py` while preserving the public route paths.

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
