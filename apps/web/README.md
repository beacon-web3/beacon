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
- `/signup`: Placeholder for the future signup flow.
- `/login`: Placeholder for the future login flow.

The signup and login buttons on the landing page route to placeholder pages until authentication is implemented.

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

The current test setup uses Playwright with Chromium and starts the Nuxt dev server automatically. E2E tests are intentionally not part of the pre-commit hook because they are slower than staged-file linting.

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
