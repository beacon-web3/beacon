# Changelog

All notable product, documentation, architecture, API, contract, and launch
changes should be recorded here.

This project follows a lightweight changelog format inspired by Keep a
Changelog. Use date-based entries until formal versioning starts.

## Unreleased

### Added

- Added local console email backend support for manual auth testing and Django
  admin visibility/actions for email verification metadata and resending
  verification codes to unverified accounts.
- Added a proposed MVP free hosting decision and implementation plan covering
  Vercel frontend hosting, Render or Cloud Run Django hosting, Neon or Aiven
  PostgreSQL hosting, production environment setup, and manual blockers for
  provider accounts and Solana event monitoring architecture.
- Documented the recommended MVP hosting stack as Vercel for Nuxt, Render for
  Django, and Aiven PostgreSQL, including rationale, alternatives, Solana
  indexing boundaries, and a later self-hosting migration shape.
- Added public backend Swagger/OpenAPI documentation with `drf-spectacular`,
  generated schema output at `/api/schema/`, Swagger UI at
  `/api/docs/swagger/`, ReDoc at `/api/docs/redoc/`, auth endpoint schema
  annotations, and regression coverage.
- Added Google social auth with backend-owned OAuth/OIDC exchange,
  `django-allauth` provider storage, verified-email account linking, social-only
  account creation with generated usernames, Nuxt login/signup controls, a
  session-confirming dashboard target, API docs, and an auth strategy decision
  record.

### Changed

- Hardened Google social auth remediation by routing provider exchange/extraction
  through allauth, enforcing strict verified Google identity normalization,
  explicitly reactivating inactive accounts only after verified proof, expanding
  backend regression coverage, and renaming the backend callback module as
  Google-specific.

## 2026-06-26

### Added

- Added backend auth localization for English/French language negotiation,
  localized auth validation/detail messages, localized auth emails, French Django
  message catalogs, and Nuxt auth API `Accept-Language` forwarding.
- Added backend auth hardening with captcha-before-duplicate signup validation,
  case-insensitive account uniqueness constraints, auth request throttles, CSRF
  regression coverage, and configurable production cookie/HTTPS/email settings.
- Added a portable backend PostgreSQL test runner that starts the Compose
  database service before running pytest from the local virtual environment or
  API container.
- Added browser-session CSRF token issuance for successful login and email
  verification, a shared Nuxt backend API transport for CSRF headers, frontend
  reCAPTCHA v2 Invisible execution, and Playwright coverage for auth request
  CSRF/reCAPTCHA behavior and password reset confirmation.
- Added and completed an auth test split plan covering backend auth API tests and
  frontend auth Playwright tests.
- Added a runtime toolchain upgrade plan for future Python, Node.js, and pnpm
  upgrades with separate verification patches.

### Changed

- Completed integrated runtime toolchain verification across Node.js `v24.16.0`,
  pnpm `11.9.0`, local Python `3.14.6`, and Docker Python
  `python:3.14.6-slim`; frontend install/lint/typecheck/build/E2E, local
  backend checks/Ruff/PostgreSQL tests, and Docker build/check/migrate/Ruff/pytest
  all passed.
- Aligned the backend Docker runtime image from `python:3.10-slim` to
  `python:3.14.6-slim`; the no-cache image build, containerized Django checks,
  migrations, Ruff checks, and pytest suite passed under Python `3.14.6`.
- Applied the backend local Python runtime target update from `3.10.10` to
  `3.14.6` across the local pin, backend setup docs, CI Python setup, and Ruff
  target, including the required Python 3.14 Ruff formatter update and
  `psycopg[binary]` packaging for fresh local virtual environments; Django,
  Ruff, and PostgreSQL-backed tests pass under Python `3.14.6`.
- Updated the frontend pnpm package-manager pin and CI installer from `11.5.0`
  to `11.9.0`; the frozen install, lint, typecheck, build, and E2E checks passed
  without lockfile or application dependency drift.
- Aligned the frontend CI Node.js runtime pin with the web `.nvmrc` Node.js
  `24.16.0` target; local frontend install, lint, typecheck, build, and E2E
  checks passed under Node.js `v24.16.0` with pnpm `11.5.0`.
- Updated the Nuxt frontend framework dependency batch covering Nuxt, Nuxt UI,
  Nuxt ESLint, and ESLint, with lint, typecheck, build, and route checks passing.
- Updated the low-risk frontend dependency batch covering Iconify icon sets,
  Prettier, lint-staged, Tailwind CSS, and vue-tsc, with frontend lint,
  typecheck, and build checks passing.
- Updated the frontend Playwright E2E tooling dependency to `@playwright/test`
  1.61.1, with Chromium install and E2E tests passing.
- Updated the backend Django dependency to 5.2.15, with Django system checks,
  Ruff checks, and PostgreSQL-backed tests passing.
- Updated the backend `django-environ` dependency to 0.14.0, with settings
  parsing checks and PostgreSQL-backed tests passing.
- Updated backend test tooling dependencies to pytest 9.1.1 and Ruff 0.15.20,
  with Ruff checks and PostgreSQL-backed tests passing.
- Added explicit local runtime pins for the web Node.js version and API Python
  version, with setup docs aligned to the completed dependency upgrades.
- Updated backend auth docs and configuration examples for password confirmation,
  session CSRF usage, throttle responses, email verification attempts, and email
  delivery settings.
- Hardened backend auth defaults and follow-ups by requiring authentication by
  default in DRF, explicitly marking public auth endpoints, throttling password
  reset confirmation, moving signup verification email dispatch after commit,
  using standard Django CORS middleware, and removing redundant email unique
  indexing while retaining Django's required username uniqueness.
- Tightened backend auth follow-ups by making post-commit signup verification
  email delivery best-effort, making email verification code consumption
  single-use under concurrent confirmation attempts, adding identifier-aware auth
  throttling, documenting email delivery failure behavior, and recording the
  production reCAPTCHA launch TODO.
- Improved auth error handling by preserving generic password reset and email
  verification resend responses when email delivery fails, logging reCAPTCHA
  transport/parse failures without secrets, surfacing safe API validation details
  through a shared web composable, adding localized retry copy, and making failed
  reCAPTCHA script loads retryable.
- Updated placeholder contracts, scripts, SDK, config, and types README files
  with current implementation status and boundaries.
- Split monolithic backend and frontend auth test files into focused auth,
  account, settings, and Playwright E2E modules without changing auth behavior.

### Fixed

- Fixed French backend translations for password-complexity validation and added
  regression coverage for weak-password signup errors under `Accept-Language: fr`.


## 2026-06-25

### Added

- Added a password-based Django session auth plan, API contract, and decision
  record covering signup, email-or-username login, password reset, reCAPTCHA v2
  Invisible, and reserved profile fields.
- Added the Beacon Editorial Ledger frontend design-system foundation for the
  Nuxt app, including Tailwind CSS 4 tokens, Nuxt UI theme defaults, book-first
  landing-page components, and restrained light/dark theme support.
- Added a clearer homepage narrative covering early book signals, the
  books-first participation loop, public reputation, and pre-signing ledger
  clarity.
- Added French localization for the web app.
- Added backend email verification OTP support with hashed six-digit codes,
  generic resend responses, configurable per-code attempt limits, login gating
  for unverified accounts, and API docs for verification request and confirmation
  endpoints.
- Added a dedicated Nuxt email verification form with segmented OTP confirmation,
  resend, localized copy, and redirects from signup or unverified login.
- Added trust-minimized protocol custody specs covering program-controlled
  Solana accounts, upgrade authority risk, multisig/timelock staging, custody
  dashboard requirements, and a proposed decision record.


### Changed

- Updated the Nuxt email auth form to use Nuxt UI form controls, password
  visibility toggles, and form-field help text for signup password requirements.
- Added Zod-backed Nuxt UI schema validation to auth forms, including field-level
  required, email, signup password policy, and password confirmation checks.
- Refactored the Nuxt email auth form to move submission state into a composable,
  remove reserved wallet/reputation helper copy from the form body, and show
  signup password requirements progressively.
- Replaced the web app's warm parchment color system with a minimal digital
  palette using off-white surfaces, deep navy ink, cyan accents, and clean
  blue-black dark mode surfaces.
- Redesigned the homepage as a sparse early-adopter landing page with a short
  Nuxt UI hero badge, live signal preview, focused reasons, simplified product
  loop, ledger clarity, and final early-access CTA.
- Reframed web starter copy toward books-first discovery and public reputation,
  avoiding passive-yield, guaranteed-return, and profit-first language.
- Replaced the Persian web locale with French and updated localized navigation,
  documentation, and smoke-test expectations.

## 2026-06-21

### Added

- Added product documentation for Beacon's books-first discovery marketplace,
  governance, treasury, risks, staking, rewards, and whitepaper outline.
- Added documentation governance files for decision records, open questions,
  assumptions, and roadmap tracking.
- Added implementation-plan documentation for breaking larger features into
  smaller tasks with acceptance criteria and verification steps.
- Added agent instructions requiring future agents to consult canonical specs
  and maintain decision records, plans, assumptions, open questions, and the
  changelog for significant work.

### Changed

- Updated project guidance to frame Beacon as a discovery and reputation network
  rather than a passive yield or guaranteed-return product.
- Updated the login and signup pages to use the same minimal Beacon visual
  system, early-access copy, and shared email access panel.
- Pinned the frontend CI workflow to pnpm 11.5.0 so GitHub Actions can install
  dependencies from the app-local web package metadata.
