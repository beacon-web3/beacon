# Beacon Web

Frontend workspace for Beacon.

This app uses Nuxt, Nuxt UI, Nuxt i18n, TypeScript, ESLint, Prettier, lint-staged, and Playwright. Frontend dependencies are managed locally in this directory with pnpm.

## Local Setup

Run these commands from `apps/web/`.

This workspace uses pnpm. Do not run Yarn commands here; `package.json` intentionally declares `"packageManager": "pnpm@11.5.0"`.

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Start Development Server

```bash
pnpm dev
```

The app starts at `http://localhost:3000` by default.

## Pages

Current pages:

- `/`: Beacon landing page explaining the discovery marketplace concept.
- `/fr`: French version of the Beacon landing page.
- `/signup`: Email-based early-access signup page.
- `/login`: Email-based login page for returning early-access accounts.
- `/verify-email`: Email verification page for six-digit OTP confirmation and
  resend requests.
- `/reset-password`: Password reset request page.
- `/reset-password/confirm`: Password reset confirmation page for Django reset
  links.

The signup and login pages use the same minimal Beacon visual system as the
landing page. Current access is email-only; wallet onboarding comes later before
any Solana signing flow.

## Auth API Runtime Configuration

The auth UI uses `NUXT_PUBLIC_API_BASE_URL` to reach the Django API. Unsafe auth
API requests include `credentials: 'include'` and send `X-CSRFToken` when the
Django `csrftoken` cookie is present.

Set `NUXT_PUBLIC_RECAPTCHA_SITE_KEY` when backend reCAPTCHA is enabled. When the
site key is empty, auth forms submit an empty token so local development can run
with backend `RECAPTCHA_ENABLED=false`.

## Internationalization

Nuxt i18n is configured with `prefix_except_default` routing:

- English: default locale, no URL prefix.
- French: `/fr` URL prefix and LTR document direction.

Translation files live in `i18n/locales/`:

- `i18n/locales/en.json`
- `i18n/locales/fr.json`

Use translation keys for user-facing copy instead of hardcoding text in Vue templates.

## Quality Checks

### Lint Frontend Files

```bash
pnpm lint
```

### Typecheck Frontend Files

```bash
pnpm typecheck
```

### Run Staged-File Checks

```bash
pnpm lint-staged
```

This is what the root pre-commit hook runs when staged files exist under `apps/web/`.

## Tests

### Install Playwright Browsers

Run this once after installing dependencies, or whenever Playwright asks for browsers to be installed:

```bash
pnpm exec playwright install chromium
```

### Run End-to-End Tests

```bash
pnpm test:e2e
```

### Run End-to-End Tests With UI

```bash
pnpm test:e2e:ui
```

The current test setup uses Playwright with Chromium and starts the Nuxt dev server automatically. E2E coverage includes the landing page, narrow mobile layout, French route, signup/login email form behavior, email verification, password reset request, password reset confirmation, CSRF header attachment, and reCAPTCHA token inclusion. E2E tests are intentionally not part of the pre-commit hook because they are slower than staged-file linting.

## Formatting

Prettier is configured in `.prettierrc.json` and is applied by lint-staged for staged CSS, JSON, Markdown, YAML, and YML files.

ESLint auto-fixes staged JavaScript, TypeScript, and Vue files.

## Current Status

- Nuxt app generated: yes
- Frontend package manager: pnpm in `apps/web/`
- Root monorepo package manager: not configured yet
- Pre-commit frontend checks: delegated from root `.husky/pre-commit`
- E2E test runner: Playwright
- Supported locales: English and French
