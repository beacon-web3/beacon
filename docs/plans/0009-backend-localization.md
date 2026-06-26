# Backend Localization

Status: Completed

## Context

The web app already supports English and French through Nuxt i18n. Backend auth
API responses, validation messages, and generated auth emails are still mostly
English-only, even though Django i18n is enabled with `USE_I18N = True`.

Relevant specs and docs:

- `docs/api/openapi.md`
- `docs/development/testing.md`
- `docs/plans/0003-homepage-clarity-localization.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0006-email-verification-otp.md`
- `docs/plans/0007-backend-auth-hardening.md`
- `docs/plans/0008-auth-error-handling.md`

## Decisions

- Use Django's built-in translation system instead of adding a custom backend
  message catalog or third-party i18n dependency.
- Negotiate backend response language from the HTTP `Accept-Language` header.
- Keep `en` as the backend default language and add `fr` as the supported French
  locale to match the frontend.
- Preserve machine-readable API fields and codes, including
  `EMAIL_VERIFICATION_REQUIRED`; localize only human-facing text.
- Do not make frontend logic depend on translated response text.
- Include backend-generated auth email subjects and bodies in localization scope.

## Tasks

- [x] Configure Django locale support.
  - Add `LANGUAGES` for English and French in `apps/api/beacon_api/settings.py`.
  - Add `LOCALE_PATHS = [BASE_DIR / "locale"]`.
  - Add `django.middleware.locale.LocaleMiddleware` after
    `django.contrib.sessions.middleware.SessionMiddleware` and before
    `django.middleware.common.CommonMiddleware`.
  - Acceptance: Django selects French for supported requests with
    `Accept-Language: fr` and falls back to English for unsupported or missing
    language headers.
  - Verify: Add or update backend tests that assert active language negotiation.

- [x] Send the frontend locale to the backend API.
  - Update `apps/web/app/composables/useApiFetch.ts` to read the current Nuxt i18n
    locale and set `Accept-Language` on backend requests when the caller has not
    already provided one.
  - Acceptance: API requests made from English pages send `Accept-Language: en`,
    and API requests made from French pages send `Accept-Language: fr`.
  - Verify: Add or update frontend tests for the shared API transport header
    behavior.

- [x] Mark backend auth API messages for translation.
  - Update user-facing strings in `apps/api/accounts/serializers.py` to use
    Django translation functions.
  - Update user-facing response detail strings in `apps/api/accounts/views.py` to
    use Django translation functions.
  - Keep logs, internal codes, and non-user-facing operational strings in English.
  - Acceptance: Validation errors and `detail` responses are emitted in the
    active request language without changing response shape.
  - Verify: Add backend API tests for representative English and French
    validation/detail responses.

- [x] Localize backend-generated auth emails.
  - Translate email verification subject/body in
    `send_email_verification_code()`.
  - Translate password reset subject/body in
    `send_password_reset_email_best_effort()`.
  - Keep OTPs, reset URLs, and security-sensitive tokens unchanged.
  - Acceptance: Auth email subject and body text use the active request language
    while preserving links, OTPs, and generic account-enumeration protections.
  - Verify: Add tests that inspect the in-memory Django mail outbox for English
    and French email content.

- [x] Generate and compile the French backend catalog.
  - Manually created `apps/api/locale/fr/LC_MESSAGES/django.po` for the scoped
    auth strings instead of running broad `makemessages` output into this change.
  - Translate generated strings in `apps/api/locale/fr/LC_MESSAGES/django.po`.
  - Run `django-admin compilemessages` from `apps/api/`.
  - Acceptance: `django.po` contains French translations for backend auth API and
    email strings, and compiled `django.mo` files are committed for runtime use.
  - Verify: Run the backend localization tests with `Accept-Language: fr`.

- [x] Document the API localization contract.
  - Update `docs/api/openapi.md` to document `Accept-Language` negotiation,
    supported backend languages, fallback behavior, and the rule that clients
    must use machine-readable fields rather than translated text for control
    flow.
  - Update `docs/development/testing.md` if new backend or frontend localization
    test commands are added.
  - Acceptance: Future API consumers know how to request localized backend text
    and which response fields remain stable.
  - Verify: Documentation review against the implemented behavior.

- [x] Update plan status and changelog after implementation verification.
  - Mark completed tasks in this plan.
  - Add a `CHANGELOG.md` entry summarizing backend French localization support.
  - Acceptance: The plan accurately reflects final implementation and verified
    commands.
  - Verify: Review the final diff for code, tests, docs, locale files, and
    changelog consistency.

## Acceptance Criteria

- Backend API responses default to English when no supported language is
  requested.
- Backend API responses return French human-facing validation and detail messages
  when `Accept-Language: fr` is sent.
- Backend-generated auth emails use English or French according to the active
  request language.
- Machine-readable API fields, error object shapes, validation field names, and
  stable codes remain unchanged.
- The frontend sends its active Nuxt locale to the backend through
  `Accept-Language` for shared API requests.
- Unsupported languages fall back to English.
- Tests cover both default English behavior and French behavior for representative
  API and email paths.
- API documentation explains localization negotiation and the translated-text
  stability boundary.

## Verification

- `cd apps/api && ./scripts/test-postgres.sh tests/test_auth_api.py`
- `cd apps/api && ./.venv/bin/python -m ruff check .`
- `cd apps/web && pnpm lint`
- `cd apps/web && pnpm typecheck`
- Run targeted frontend tests for `useApiFetch` if added or updated.
- Manually inspect `apps/api/locale/fr/LC_MESSAGES/django.po` for complete French
  translations before compiling catalogs.

Completed checks:

- `cd apps/api && ./scripts/test-postgres.sh tests/test_auth_api.py -k 'language_negotiation or uses_french_response'`
- `cd apps/api && ./scripts/test-postgres.sh tests/test_auth_api.py`
- `cd apps/api && ./.venv/bin/python -m ruff check .`
- `cd apps/web && pnpm lint`
- `cd apps/web && pnpm typecheck`
- `cd apps/web && pnpm test:e2e tests/e2e/auth.spec.ts`

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Frontend behavior depends on English message text | Medium | Preserve stable codes/field names and update docs to prohibit translated text control flow. |
| Account-enumeration protections regress in reset or verification flows | High | Keep generic response semantics unchanged and test English/French variants. |
| Locale activation does not apply to async/on-commit email sending | Medium | Translate email strings before sending in the request context or explicitly activate the intended language when sending. |
| Generated compiled catalogs are omitted from deployment artifacts | Medium | Decide whether compiled `.mo` files are committed or generated during build, then document and verify that path. |
| Unsupported locale headers produce inconsistent fallbacks | Low | Limit `LANGUAGES` to `en` and `fr`, and test unsupported header fallback. |

## Resolved Questions

- Compiled `.mo` files are committed so runtime deployments and tests do not
  depend on a separate catalog compilation step.
- Backend localized strings use a neutral/formal French tone for auth flows.
