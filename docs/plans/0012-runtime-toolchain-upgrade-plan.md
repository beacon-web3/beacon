# Runtime Toolchain Upgrade Plan

Status: Draft

## Context

Beacon currently pins local and package-manager runtime versions separately from
application dependencies:

- `apps/web/.nvmrc` pins Node.js `24.16.0`.
- `apps/web/package.json` declares `"packageManager": "pnpm@11.5.0"`.
- `apps/api/.python-version` pins local Python `3.10.10`.
- `apps/api/Dockerfile` uses the `python:3.10-slim` Docker runtime family.

This plan upgrades Python, Node.js, and pnpm without changing product behavior,
auth behavior, tokenomics, treasury assumptions, staking behavior, governance
policy, or Solana transaction behavior.

## Guardrails

- Do not combine Python, Node.js, and pnpm upgrades in one patch.
- Do not combine runtime upgrades with application library upgrades unless a
  runtime requires a lockfile-only refresh.
- Do not introduce `uv` as part of this plan unless separately approved.
- Do not change Beacon product, treasury, governance, staking, reward, or Solana
  behavior while upgrading runtimes.
- Keep source changes limited to verified compatibility fixes required by a
  failing check.
- Record exact versions chosen during execution before marking any patch
  complete.

## Open Version Decisions

Select target versions before implementation starts:

- Node.js target: Node.js 24.16.0 (LTS)
- pnpm target: check if pnpm version v11.9.0 is compatible with the selected Node runtime and upgrade
- Python target: Python 3.14.6
- Docker base image target: align with the selected Python runtime using a
  specific supported `python:<version>-slim` family.

## Patch 0: Baseline Runtime Verification

Status: Verified with documented E2E blocker.

Description: Verify the repository is green under the current runtime pins before
changing any toolchain versions.

Expected file changes:

- None.

Acceptance criteria:

- Current Node, pnpm, Python, and Docker runtime versions are recorded.
- Frontend install, lint, typecheck, build, and E2E tests pass under the current
  pins.
- Backend system checks, Ruff checks, format checks, and PostgreSQL-backed tests
  pass under the current pins.
- Any pre-existing failure is documented before runtime upgrade work starts.

Verification:

From `apps/web`:

```bash
node --version
pnpm --version
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
```

From `apps/api`:

```bash
.venv/bin/python --version
docker compose run --rm api python --version
.venv/bin/python manage.py check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
./scripts/test-postgres.sh
```

Dependencies: None.

Risk controls:

- Do not proceed if baseline verification is red unless the failure is documented
  and explicitly accepted as unrelated.
- Do not update dependency manifests or lockfiles in this patch.

Execution notes:

- Verified on 2026-06-26 under current pins: Node.js `v24.16.0`, pnpm `11.5.0`,
  local Python `3.10.10`, Docker image `python:3.10-slim` reporting Python
  `3.10.20` at runtime.
- Frontend passed: `pnpm install --frozen-lockfile`, `pnpm lint`,
  `pnpm typecheck`, and `pnpm build`.
- Frontend E2E did not run because Playwright found `http://127.0.0.1:3000`
  already in use by a pre-existing `node` process (`PID 60948`).
- Backend passed: `.venv/bin/python manage.py check`, `.venv/bin/ruff check .`,
  `.venv/bin/ruff format --check .`, and `./scripts/test-postgres.sh`
  (`70 passed`).

## Patch 1: Node.js Runtime Upgrade

Status: Applied with documented local verification blockers.

Description: Upgrade the frontend Node.js runtime pin independently from pnpm and
application libraries.

Expected file changes:

- `apps/web/.nvmrc`
- `apps/web/README.md`
- CI/runtime documentation or workflow files only if they currently pin Node.js.

Acceptance criteria:

- `.nvmrc` and frontend setup documentation agree on the selected Node.js
  version.
- Existing `packageManager` remains unchanged in this patch unless the selected
  Node.js version cannot run the existing pnpm version.
- Frontend install, lint, typecheck, build, and E2E tests pass under the selected
  Node.js version.
- No frontend source changes are made unless required by a verified runtime
  compatibility failure.

Verification from `apps/web`:

```bash
node --version
corepack enable
pnpm --version
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
```

Dependencies: Patch 0 and resolved Node.js target decision.

Risk controls:

- Review Nuxt, Vite/Nitro, TypeScript, Playwright, and pnpm engine support before
  selecting a Node.js major version.
- Prefer an LTS runtime for broad tooling compatibility unless the team explicitly
  chooses the current line.
- Keep pnpm version changes for Patch 2 unless Node.js compatibility blocks
  verification.

Execution notes:

- Applied on 2026-06-26 with selected Node.js target `24.16.0`.
- `apps/web/.nvmrc` and `apps/web/README.md` already matched Node.js `24.16.0`.
- Updated `.github/workflows/ci.yml` frontend `actions/setup-node` pin from Node
  `22` to `24.16.0` so CI matches the local runtime pin.
- Kept `apps/web/package.json` package manager unchanged at `pnpm@11.5.0` for
  Patch 2.
- Verified local runtime and package manager: Node.js `v24.16.0`, pnpm `11.5.0`.
- `corepack enable` was blocked by a local Corepack shim error resolving missing
  `/usr/local/bin/yarn`; `corepack enable pnpm` succeeded.
- Passed: `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm typecheck`, and
  `pnpm build` from `apps/web`.
- `pnpm test:e2e` did not run because Playwright found
  `http://127.0.0.1:3000` already in use by pre-existing Nuxt dev server process
  `PID 60948`, and `playwright.config.ts` has `reuseExistingServer: false`.

## Patch 2: pnpm Upgrade

Status: Not started.

Description: Upgrade the frontend package manager after the Node.js runtime is
stable.

Expected file changes:

- `apps/web/package.json`
- `apps/web/pnpm-lock.yaml`
- `apps/web/README.md`
- CI workflow files only if they pin pnpm.

Acceptance criteria:

- `packageManager` declares the selected pnpm version.
- Lockfile changes are limited to pnpm metadata and resolver changes caused by
  the pnpm upgrade; application dependency versions should not drift unless the
  change is explicitly documented.
- Frontend install, lint, typecheck, build, and E2E tests pass under the selected
  Node.js and pnpm versions.
- Known peer dependency warnings are documented and not silently resolved by
  unrelated application dependency updates.

Verification from `apps/web`:

```bash
corepack prepare pnpm@<target> --activate
pnpm --version
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
pnpm peers check
```

Dependencies: Patch 1 and resolved pnpm target decision.

Risk controls:

- If pnpm changes lockfile format, verify CI and all developer setup docs support
  the new pnpm version before committing the lockfile.
- Do not use `pnpm update` for application packages in this patch.
- If `pnpm install --frozen-lockfile` fails because the lockfile format must be
  refreshed, run a non-frozen install once and inspect the lockfile diff closely.

## Patch 3: Python Local Runtime Upgrade

Status: Not started.

Description: Upgrade the local backend Python runtime pin and verify the backend
under that interpreter before changing Docker.

Expected file changes:

- `apps/api/.python-version`
- `apps/api/README.md`
- Backend tooling or CI documentation only if it currently pins local Python.

Acceptance criteria:

- `.python-version` and backend setup documentation agree on the selected Python
  version.
- Backend requirements install successfully under the selected Python version.
- Django system checks, Ruff checks, format checks, and PostgreSQL-backed tests
  pass under the selected Python version.
- No Python source changes are made unless required by a verified runtime
  compatibility failure.

Verification from `apps/api`:

```bash
python --version
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python manage.py check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
./scripts/test-postgres.sh
```

Dependencies: Patch 0 and resolved Python target decision.

Risk controls:

- Check Django, DRF, psycopg, pytest, Ruff, and any transitive binary package
  support before selecting a newer Python version.
- If the virtual environment is recreated, do not commit `.venv` artifacts.
- Keep Docker base-image changes for Patch 4.

## Patch 4: Python Docker Runtime Upgrade

Status: Not started.

Description: Align the backend container runtime with the selected Python runtime
after local backend verification is green.

Expected file changes:

- `apps/api/Dockerfile`
- `apps/api/README.md`
- CI/deployment files only if they pin the backend Python image.

Acceptance criteria:

- Dockerfile uses the selected supported Python slim image.
- Backend image builds successfully.
- Migrations, Ruff checks, and tests pass inside Docker.
- Local `.python-version`, Dockerfile, and README guidance do not conflict.

Verification from `apps/api`:

```bash
docker compose build --no-cache api
docker compose run --rm api python --version
docker compose run --rm api python manage.py check
docker compose run --rm api python manage.py migrate
docker compose run --rm api ruff check .
docker compose run --rm api pytest
```

Dependencies: Patch 3.

Risk controls:

- Use a supported official Python image tag rather than an unpinned floating major
  tag.
- Confirm package installation still works from `requirements-dev.txt` in the
  container before changing application code.
- Do not combine Docker Compose service behavior changes with this runtime image
  update.

## Patch 5: Full Toolchain Integration Verification

Status: Not started.

Description: Verify the upgraded Node.js, pnpm, local Python, and Docker Python
runtimes together after each independent patch is green.

Expected file changes:

- None, unless a verified documentation correction is required.

Acceptance criteria:

- Frontend install, lint, typecheck, build, and E2E tests pass with the selected
  Node.js and pnpm versions.
- Backend local checks and PostgreSQL-backed tests pass with the selected local
  Python version.
- Backend Docker build, migrations, Ruff checks, and tests pass with the selected
  Docker Python runtime.
- README setup guidance matches the final selected versions.
- `CHANGELOG.md` summarizes only checks that actually ran.

Verification:

From `apps/web`:

```bash
node --version
pnpm --version
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
```

From `apps/api`:

```bash
.venv/bin/python --version
.venv/bin/python manage.py check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
./scripts/test-postgres.sh
docker compose build --no-cache api
docker compose run --rm api pytest
```

Dependencies: Patches 1 through 4.

Risk controls:

- If final integration fails, bisect by runtime patch rather than making broad
  compatibility edits.
- Keep final documentation edits factual and limited to versions and checks that
  were actually verified.

## Recommended Session Boundaries

- Session 1: Patch 0 only.
- Session 2: Decide and apply Patch 1 for Node.js.
- Session 3: Patch 2 for pnpm after Node.js is green.
- Session 4: Decide and apply Patch 3 for local Python.
- Session 5: Patch 4 for Docker Python after local Python is green.
- Session 6: Patch 5 integration verification and final documentation/changelog.

## Overall Acceptance Criteria

- Runtime and package-manager pins are explicit and consistent across setup docs,
  manifests, and Docker files.
- Frontend behavior remains unchanged after Node.js and pnpm upgrades.
- Backend behavior remains unchanged after Python local and Docker runtime
  upgrades.
- Runtime upgrades are independently verifiable and rollback-friendly.
- Documentation and changelog entries describe actual completed work, not planned
  work.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Node.js target is unsupported by Nuxt, Nitro, Playwright, or pnpm | High | Check engine support and run full frontend verification before pnpm changes. |
| pnpm lockfile format changes unexpectedly | Medium | Isolate pnpm in its own patch and inspect lockfile-only diffs. |
| Python target is unsupported by Django, DRF, psycopg, or test tooling | High | Verify package support before changing pins and run local backend tests first. |
| Docker Python image differs from local Python behavior | Medium | Upgrade Docker after local Python, then run containerized migrations and tests. |
| Runtime upgrades get mixed with library upgrades | High | Keep application dependency upgrades out of this plan unless separately approved. |
| Documentation claims unverified runtime support | Medium | Update docs only after checks run and record exact commands in execution notes. |

## Questions

- Which Node.js target should Beacon standardize on for the next cycle? Node.js 24.16.0 (LTS)
- Which pnpm version should be paired with the selected Node.js target? v11.9.0
- Which Python version should Beacon backend move to? Python 3.14.6 after compatibility review
- Should Docker use an exact patch image tag or stay on a supported minor-family
  slim tag such as `python:3.12-slim`? use the exact patch slim tag: python:3.14.6-slim, assuming that official image exists and compatibility checks pass.
