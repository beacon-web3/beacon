# Auth Entry UI Refresh

## Status

Completed

## Context

The login and signup pages were still using a generic card treatment while the
homepage had moved to a sparse, minimal Beacon visual system for early adopters.
The auth entry pages needed to feel like part of the same product surface without
changing the underlying email-only API behavior.

## Source Docs

- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/architecture/system-design.md`
- `docs/api/openapi.md`
- `docs/plans/completed/0002-frontend-design-system.md`
- `docs/plans/completed/0003-homepage-clarity-localization.md`

## Scope

- Refresh the shared login/signup form UI to match the minimal Beacon homepage.
- Keep `/login` and `/signup` as thin page wrappers around the shared auth form.
- Preserve the existing email-only auth endpoints, request payloads, success
  messages, error handling, and signup clear-on-success behavior.
- Add English and French auth copy for the shared form.
- Keep wallet onboarding framed as a later step before Solana signing.

## Tasks

- [x] Redesign `EmailAuthForm.vue` with Beacon layout, typography, token colors,
  Nuxt UI badge/buttons, and accessible status/error states.
- [x] Add complete English and French auth translation keys.
- [x] Preserve the existing email POST behavior for signup and login.
- [x] Update documentation for current auth entry pages and E2E coverage.
- [x] Run frontend typecheck, lint, smoke E2E, and auth E2E verification.

## Acceptance Criteria

- Login and signup pages visually align with the minimal homepage design system.
- Auth copy avoids yield, profit, or investment framing.
- Email form labels, submit buttons, success states, and error alerts remain
  accessible to Playwright and assistive technologies.
- Signup and login continue to POST `{ "email": "..." }` to the existing auth
  endpoints.
- English and French auth routes use translation keys instead of hardcoded text.
- Targeted frontend verification passes.

## Verification

Run from the repository root:

```sh
pnpm --dir apps/web typecheck
pnpm --dir apps/web lint
pnpm --dir apps/web exec playwright test tests/e2e/smoke.spec.ts tests/e2e/auth.spec.ts
```

All verification commands passed on 2026-06-21.
