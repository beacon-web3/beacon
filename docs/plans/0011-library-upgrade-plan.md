# Library Upgrade Plan

Status: Draft

## Context

Beacon has separate frontend and backend dependency surfaces:

- `apps/web` uses pnpm with `package.json` and `pnpm-lock.yaml`.
- `apps/api` uses Python requirements files with `requirements.txt` and
  `requirements-dev.txt`.

The goal is to upgrade libraries without changing product behavior, auth
behavior, tokenomics, treasury assumptions, staking behavior, governance policy,
or Solana transaction behavior. Each patch should be small enough to complete and
verify in a separate session.

Relevant project files:

- `apps/web/package.json`
- `apps/web/pnpm-lock.yaml`
- `apps/web/nuxt.config.ts`
- `apps/web/playwright.config.ts`
- `apps/web/README.md`
- `apps/api/requirements.txt`
- `apps/api/requirements-dev.txt`
- `apps/api/pyproject.toml`
- `apps/api/Dockerfile`
- `apps/api/compose.yaml`
- `apps/api/scripts/test-postgres.sh`
- `apps/api/README.md`

Current dependency management constraints:

- Do not introduce `uv` during this upgrade unless separately approved.
- Do not combine Python or Node runtime migration with dependency upgrades.
- Do not combine frontend and backend dependency upgrades in the same patch.
- Do not make source changes unless a dependency upgrade forces a minimal,
  verified compatibility fix.
- Do not update product specs, tokenomics, treasury, governance, staking, or
  Solana contract behavior as part of this plan.

## Known Dependency Targets

Frontend packages identified for upgrade:

| Package | Current | Target |
| --- | --- | --- |
| `@iconify-json/lucide` | `1.2.111` | `1.2.114` |
| `@iconify-json/simple-icons` | `1.2.84` | `1.2.87` |
| `@nuxt/ui` | `4.8.1` | `4.9.0` |
| `@nuxt/eslint` | `1.15.2` | `1.16.0` |
| `@playwright/test` | `1.60.0` | `1.61.1` |
| `eslint` | `10.4.1` | `10.5.0` |
| `lint-staged` | `17.0.7` | `17.0.8` |
| `nuxt` | `4.4.6` | `4.4.8` |
| `prettier` | `3.8.3` | `3.8.4` |
| `tailwindcss` | `4.3.0` | `4.3.1` |
| `vue-tsc` | `3.3.3` | `3.3.5` |

Backend packages identified for upgrade:

| Package | Current | Target |
| --- | --- | --- |
| `Django` | `5.2.14` | `5.2.15` |
| `django-environ` | `0.13.0` | `0.14.0` |
| `pytest` | `9.0.3` | `9.1.1` |
| `ruff` | `0.15.15` | `0.15.20` |

Backend packages already at latest during planning:

- `djangorestframework==3.17.1`
- `django-cors-headers==4.9.0`
- `psycopg==3.3.4`
- `factory_boy==3.3.3`
- `pytest-django==4.12.0`

## Decisions

- Treat this as a dependency maintenance plan, not a feature plan.
- Keep each patch independently verifiable and safe to run in a separate session.
- Use the existing pnpm workflow for the frontend.
- Use the existing requirements-file and Docker Compose workflow for the backend.
- Run baseline checks before changing versions.
- Keep framework-coupled frontend packages together: Nuxt, Nuxt UI, Nuxt ESLint,
  and ESLint.
- Keep Playwright separate from the Nuxt framework batch so test-runner changes
  are isolated.
- Keep Django separate from backend test tooling so runtime behavior changes are
  isolated from test-runner and lint changes.
- Add runtime version pinning only as a separate patch after dependency patches
  are green.

## Patch 0: Baseline Verification

Status: Completed on 2026-06-26.

Description: Verify the current repository state before dependency changes. This
patch should not change dependency manifests, lockfiles, application code, or
documentation except for recording a separate blocker if the baseline is already
red.

Expected file changes:

- None.

Acceptance criteria:

- Current frontend lockfile installs cleanly.
- Current frontend lint, typecheck, and build pass.
- Current backend Ruff checks pass.
- Current backend PostgreSQL-backed tests pass.
- Any pre-existing failure is documented before upgrade work starts.

Verification:

Frontend from `apps/web`:

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
```

Backend from `apps/api`:

```bash
python -m pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/ruff format --check .
./scripts/test-postgres.sh
```

Dependencies: None.

Execution notes:

- Frontend baseline passed on 2026-06-26 with `pnpm install --frozen-lockfile`,
  `pnpm lint`, `pnpm typecheck`, and `pnpm build` from `apps/web`.
- Backend baseline passed on 2026-06-26 from `apps/api` using the existing
  virtualenv: requirements install, Ruff check, Ruff format check, and
  `./scripts/test-postgres.sh`.
- The literal `python -m pip install -r requirements-dev.txt` command failed in
  this local shell because `python` is not on `PATH`; the existing `.venv` Python
  was used instead. Backend PostgreSQL-backed tests passed with 70 tests.

Risk controls:

- Do not begin upgrades if the baseline is red.
- Do not mix baseline fixes with dependency upgrades.
- Confirm Docker is running before backend test verification.
- If `.venv` does not exist, use the documented Docker fallback or create the
  environment in a separate setup step before this plan continues.

## Patch 1: Frontend Low-Risk Patch Updates

Status: Completed on 2026-06-26.

Description: Upgrade frontend packages with low expected framework risk before
touching Nuxt, Nuxt UI, ESLint, or Playwright.

Packages:

- `@iconify-json/lucide`: `1.2.111` to `1.2.114`
- `@iconify-json/simple-icons`: `1.2.84` to `1.2.87`
- `prettier`: `3.8.3` to `3.8.4`
- `lint-staged`: `17.0.7` to `17.0.8`
- `tailwindcss`: `4.3.0` to `4.3.1`
- `vue-tsc`: `3.3.3` to `3.3.5`

Expected file changes:

- `apps/web/package.json`
- `apps/web/pnpm-lock.yaml`

Acceptance criteria:

- Only this package batch changes in frontend dependency files.
- Frontend lint passes.
- Frontend typecheck passes.
- Frontend build passes.
- No app source changes are made unless required by a verified compatibility
  issue.

Verification from `apps/web`:

```bash
pnpm update @iconify-json/lucide @iconify-json/simple-icons prettier lint-staged tailwindcss vue-tsc --latest
pnpm lint
pnpm typecheck
pnpm build
```

Dependencies: Patch 0.

Execution notes:

- Updated the planned frontend low-risk package batch on 2026-06-26 with
  `pnpm update @iconify-json/lucide @iconify-json/simple-icons prettier lint-staged tailwindcss vue-tsc --latest`
  from `apps/web`.
- Direct package updates were limited to `@iconify-json/lucide`,
  `@iconify-json/simple-icons`, `prettier`, `lint-staged`, `tailwindcss`, and
  `vue-tsc` in `apps/web/package.json`.
- Frontend verification passed with `pnpm lint`, `pnpm typecheck`, and
  `pnpm build` from `apps/web`.
- `pnpm peers check` reported an unmet transitive Tiptap peer warning
  (`@tiptap/extension-collaboration@3.24.0` wants `@tiptap/y-tiptap@^3.0.4`,
  installed `3.0.3`); no Patch 1 direct dependency was changed to resolve it.

Risk controls:

- Keep Nuxt, Nuxt UI, Nuxt ESLint, ESLint, and Playwright out of this patch.
- If Tailwind output changes unexpectedly, isolate whether the Tailwind patch is
  the cause before continuing.
- Do not apply broad formatting changes beyond files directly touched by the
  patch.

## Patch 2: Frontend Nuxt Framework Batch

Status: Completed on 2026-06-26.

Description: Upgrade Nuxt ecosystem packages together because their peer
dependencies and generated configuration are coupled.

Packages:

- `nuxt`: `4.4.6` to `4.4.8`
- `@nuxt/ui`: `4.8.1` to `4.9.0`
- `@nuxt/eslint`: `1.15.2` to `1.16.0`
- `eslint`: `10.4.1` to `10.5.0`

Expected file changes:

- `apps/web/package.json`
- `apps/web/pnpm-lock.yaml`
- Minimal source/config compatibility changes only if required.

Acceptance criteria:

- Nuxt prepare/install succeeds.
- ESLint config still loads from `.nuxt/eslint.config.mjs`.
- Nuxt UI components render without import, theme, or generated-class errors.
- i18n routing still works for `/` and `/fr`.
- Frontend lint, typecheck, and build pass.

Verification from `apps/web`:

```bash
pnpm update nuxt @nuxt/ui @nuxt/eslint eslint --latest
pnpm install
pnpm lint
pnpm typecheck
pnpm build
```

Manual route checks after `pnpm dev`:

- `/`
- `/fr`
- `/signup`
- `/login`
- `/verify-email`
- `/reset-password`
- `/reset-password/confirm`

Dependencies: Patch 1.

Execution notes:

- Updated the planned Nuxt framework package batch on 2026-06-26 with
  `pnpm update nuxt @nuxt/ui @nuxt/eslint eslint --latest` from `apps/web`.
- Direct package updates were limited to `nuxt`, `@nuxt/ui`, `@nuxt/eslint`,
  and `eslint` in `apps/web/package.json`.
- Frontend verification passed with `pnpm install`, `pnpm lint`,
  `pnpm typecheck`, and `pnpm build` from `apps/web`.
- Manual route checks against `pnpm dev --host 127.0.0.1 --port 3000` returned
  HTTP 200 for `/`, `/fr`, `/signup`, `/login`, `/verify-email`,
  `/reset-password`, and `/reset-password/confirm`.
- `pnpm peers check` reported unmet transitive Tiptap peer warnings after the
  Nuxt UI update (`@tiptap/y-tiptap`, `@tiptap/core`, and `@tiptap/pm`); no
  Patch 2 direct dependency was changed to resolve them.
- No source or config compatibility changes were required.

Risk controls:

- Do not upgrade Playwright in this patch.
- If `pnpm typecheck` fails from generated Nuxt types, rerun `pnpm install` or
  `pnpm postinstall` before changing source code.
- Review Nuxt, Nuxt UI, and Nuxt ESLint release notes before making compatibility
  edits.
- Keep any compatibility fix minimal and tied to a failing verification command.

## Patch 3: Frontend E2E Tooling Batch

Status: Completed on 2026-06-26.

Description: Upgrade Playwright separately so browser-test-runner changes are
isolated from Nuxt framework changes.

Package:

- `@playwright/test`: `1.60.0` to `1.61.1`

Expected file changes:

- `apps/web/package.json`
- `apps/web/pnpm-lock.yaml`
- Minimal test compatibility changes only if required.

Acceptance criteria:

- Playwright Chromium installs successfully.
- Existing E2E tests pass.
- Existing `playwright.config.ts` web server behavior still works.
- No application behavior changes are made.

Verification from `apps/web`:

```bash
pnpm update @playwright/test --latest
pnpm exec playwright install chromium
pnpm test:e2e
```

Dependencies: Patch 2.

Execution notes:

- Updated `@playwright/test` from `1.60.0` to `1.61.1` on 2026-06-26 with
  `pnpm update @playwright/test --latest` from `apps/web`.
- Direct package updates were limited to `@playwright/test` in
  `apps/web/package.json`.
- Playwright Chromium installed successfully with
  `pnpm exec playwright install chromium`.
- E2E verification passed with `pnpm test:e2e` from `apps/web`: 22 tests
  passed.
- `pnpm peers check` still reports the existing transitive Tiptap peer warnings
  documented after Patch 2; no Patch 3 direct dependency was changed to resolve
  them.
- No application, test, or Playwright config compatibility changes were
  required.

Risk controls:

- Do not change app code unless an app incompatibility is proven independently
  from a Playwright timing or selector issue.
- If tests fail only due to timing or stricter Playwright behavior, keep fixes
  test-specific and minimal.
- Confirm failures are not caused by a stale running dev server before editing
  tests.

## Patch 4: Backend Django Patch Upgrade

Description: Upgrade the Django patch version alone to isolate framework runtime
behavior from backend tooling changes.

Package:

- `Django`: `5.2.14` to `5.2.15`

Expected file changes:

- `apps/api/requirements.txt`

Acceptance criteria:

- Django system checks pass.
- Full backend test suite passes against PostgreSQL.
- Auth, sessions, CSRF, throttling, email verification, and password reset tests
  remain green.
- No migrations are added unless Django detects a real model-state change.

Verification from `apps/api`:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install Django==5.2.15
python manage.py check
.venv/bin/ruff check .
./scripts/test-postgres.sh
```

Dependencies: Patch 0. This can run after frontend patches or independently once
baseline verification is complete.

Risk controls:

- Keep DRF, pytest, Ruff, and django-environ unchanged in this patch.
- Inspect Django 5.2.15 release notes before source edits.
- Do not weaken auth, CSRF, session, or throttling behavior to satisfy tests.

## Patch 5: Backend Runtime Helper Upgrade

Description: Upgrade `django-environ` separately because settings parsing affects
runtime configuration, database URLs, CORS, CSRF, and security settings.

Package:

- `django-environ`: `0.13.0` to `0.14.0`

Expected file changes:

- `apps/api/requirements.txt`
- `.env.example` only if the new version requires syntax changes.

Acceptance criteria:

- Django system checks pass.
- Environment parsing still works for booleans, lists, integers, and database
  URLs.
- Tests involving settings, CORS, CSRF, auth throttles, and database config pass.

Verification from `apps/api`:

```bash
python -m pip install django-environ==0.14.0
python manage.py check
./scripts/test-postgres.sh
```

Dependencies: Patch 4.

Risk controls:

- Do not change environment variable names.
- Do not change default runtime behavior unless required by the dependency
  update and verified by tests.
- Pay close attention to `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`,
  `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL` parsing.

## Patch 6: Backend Test Tooling Upgrade

Description: Upgrade backend development tools after runtime dependencies are
stable.

Packages:

- `pytest`: `9.0.3` to `9.1.1`
- `ruff`: `0.15.15` to `0.15.20`

Expected file changes:

- `apps/api/requirements-dev.txt`
- Minimal test or lint compatibility changes only if required.

Acceptance criteria:

- Ruff rules still pass with the current config.
- Ruff format check still passes.
- Pytest still discovers tests from `pyproject.toml`.
- PostgreSQL-backed test runner still works.

Verification from `apps/api`:

```bash
python -m pip install pytest==9.1.1 ruff==0.15.20
.venv/bin/ruff check .
.venv/bin/ruff format --check .
./scripts/test-postgres.sh
```

Dependencies: Patch 5.

Risk controls:

- Keep `pytest-django` unchanged because it was already latest during planning.
- Treat new Ruff findings as lint compatibility issues, not product behavior
  changes.
- If pytest behavior changes, avoid weakening tests; update fixtures or
  assertions only when justified by release notes or verified behavior.

## Patch 7: Runtime Version Pinning

Description: Add explicit runtime version guidance after dependency patches are
green so future installs are reproducible.

Expected file changes:

- A Node version pin such as `apps/web/.nvmrc`, or an approved repo-level tooling
  version file.
- A Python version pin such as `apps/api/.python-version`, or an approved
  repo-level tooling version file.
- README updates only if needed to keep setup docs consistent.

Suggested versions to evaluate:

- Node: `24.16.0`, matching the local runtime observed during planning, or a
  team-approved supported LTS/current version.
- Python: `3.10.x`, matching `apps/api/Dockerfile` and the local runtime observed
  during planning.

Acceptance criteria:

- Runtime pins and README setup guidance agree.
- Frontend installs and builds under the pinned Node version.
- Backend Docker image and local Python guidance do not conflict.

Verification:

```bash
node --version
pnpm --version
python3 --version
```

Frontend from `apps/web`:

```bash
pnpm install --frozen-lockfile
pnpm build
```

Backend from `apps/api`:

```bash
python -m pip install -r requirements-dev.txt
python manage.py check
```

Dependencies: Patches 1 through 6.

Risk controls:

- Do not use this patch to migrate Node or Python major versions.
- If moving backend from Python 3.10 to a newer Python version, create a separate
  migration plan.
- If choosing Node 22 LTS instead of Node 24, verify the frontend lockfile engine
  constraints first.

## Patch 8: Full Integration Verification

Description: Verify frontend and backend together after all dependency patches.
This patch is primarily verification; it should not change code unless a minimal
integration fix is required and justified by a failing check.

Expected file changes:

- None, unless a verified integration compatibility issue requires a minimal fix.

Acceptance criteria:

- Backend builds and starts through Docker Compose.
- Backend migrations apply.
- Backend tests pass in Docker or through the PostgreSQL-backed runner.
- Frontend reaches the backend API with cookies and CSRF behavior intact.
- Signup, login, email verification, password reset, and landing-page E2E tests
  pass.
- Browser console has no dependency-upgrade errors from Nuxt, Nuxt UI, i18n,
  Tailwind, or auth transport code.

Backend verification from `apps/api`:

```bash
docker compose up --build
docker compose run --rm api python manage.py migrate
docker compose run --rm api pytest
docker compose run --rm api ruff check .
```

Frontend verification from `apps/web` with backend running:

```bash
NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 pnpm dev
pnpm test:e2e
```

Dependencies: Patches 1 through 7, if runtime pinning is included. If runtime
pinning is deferred, this depends on Patches 1 through 6.

Risk controls:

- Run this only after earlier patches are independently green.
- If integration fails, bisect by patch rather than changing multiple areas at
  once.
- Keep auth and security behavior unchanged unless a dependency forces a
  documented compatibility fix.

## Patch 9: Documentation And Changelog

Description: Update dependency-version references and completion notes after
verified upgrades. Documentation should reflect actual completed work, not
planned work.

Expected file changes:

- `apps/web/README.md`
- `apps/api/README.md`
- `CHANGELOG.md`
- This plan file, to move completed tasks from unchecked to checked if the team
  wants the plan to track execution status.

Acceptance criteria:

- README dependency versions match actual manifests.
- Setup and verification commands remain accurate.
- Changelog summarizes dependency upgrades and verification actually performed.
- This plan is updated to `Completed` only after all selected patches and
  verification are complete.

Verification:

- Compare README version references against `apps/web/package.json`,
  `apps/api/requirements.txt`, and `apps/api/requirements-dev.txt`.
- Confirm the changelog does not claim checks that were not run.

Dependencies: Patch 8.

Risk controls:

- Do not update docs ahead of implementation except for this plan.
- Do not claim E2E or backend tests passed unless they actually ran.
- Do not introduce product, tokenomics, treasury, governance, staking, or Solana
  behavior changes in dependency-upgrade documentation.

## Recommended Session Boundaries

- Session 1: Patch 0 only.
- Session 2: Patch 1.
- Session 3: Patch 2.
- Session 4: Patch 3.
- Session 5: Patch 4.
- Session 6: Patch 5 and Patch 6 if Patch 5 is clean.
- Session 7: Patch 7 if runtime pinning is approved.
- Session 8: Patch 8 and Patch 9.

## Do Not Combine

- Do not combine Nuxt upgrades with Playwright upgrades.
- Do not combine Django patch upgrades with pytest or Ruff upgrades.
- Do not combine Python or Node runtime migration with dependency upgrades.
- Do not introduce `uv` during this upgrade unless separately approved.
- Do not add or change product behavior while upgrading libraries.
- Do not update Solana, tokenomics, treasury, staking, governance, or reward
  behavior as part of this plan.

## Overall Acceptance Criteria

- Frontend dependency manifests and lockfile are upgraded through small,
  independently verified patches.
- Backend requirements files are upgraded through small, independently verified
  patches.
- Existing frontend and backend behavior remains unchanged except for minimal,
  documented compatibility fixes if required.
- Frontend lint, typecheck, build, and E2E tests pass after relevant frontend
  patches.
- Backend Ruff checks, Django system checks, and PostgreSQL-backed tests pass
  after relevant backend patches.
- Runtime pinning, if approved, is handled separately from dependency upgrades.
- Documentation and changelog are updated only after verified implementation.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Baseline is already failing | High | Run Patch 0 first and do not start upgrades until baseline failures are resolved or explicitly documented. |
| Nuxt, Nuxt UI, and ESLint peer dependencies drift | High | Upgrade Nuxt ecosystem packages together in Patch 2 and verify lint, typecheck, build, and key routes. |
| Playwright upgrade causes test-runner noise that masks app issues | Medium | Keep Playwright isolated in Patch 3 and limit fixes to tests unless application behavior is proven broken. |
| Django patch changes auth, session, or CSRF behavior | High | Upgrade Django alone in Patch 4 and run the full PostgreSQL-backed backend test suite. |
| `django-environ` changes settings parsing | High | Upgrade it alone in Patch 5 and verify settings, CORS, CSRF, throttle, and database tests. |
| Ruff or pytest introduces stricter checks | Medium | Upgrade tooling after runtime patches and keep any resulting changes small and test/lint-focused. |
| Runtime version ambiguity causes inconsistent installs | Medium | Add runtime pins only after library upgrades are green and verify installs under the selected versions. |
| Documentation claims unverified work | Medium | Update README and changelog last, and only list checks that actually ran. |

## Open Questions

- Should Beacon standardize on Node `24.16.0`, Node 22 LTS, or another supported
  runtime before future frontend upgrades?
- Should backend Python remain on 3.10 for now, matching the Dockerfile, or should
  a separate Python runtime migration plan be created later?
