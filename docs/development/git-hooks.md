# Git Hooks

Beacon uses a root pre-commit hook to run fast staged-file checks before a commit is created.

The project currently keeps package managers app-local:

* Frontend tooling lives in `apps/web/` and uses pnpm.
* Backend tooling lives in `apps/api/` and uses a Python virtual environment.

## Current Hook

The tracked hook file is:

```text
.husky/pre-commit
```

It runs:

* `pnpm lint-staged` from `apps/web/` when staged files exist under `apps/web/`.
* Ruff format and lint checks when staged Python files exist under `apps/api/`.

## Enable Hooks In A Fresh Clone

Git does not track files inside `.git/hooks/`, so each clone needs to link the tracked hook once.

Run this from the repository root:

```bash
ln -s ../../.husky/pre-commit .git/hooks/pre-commit
```

If `.git/hooks/pre-commit` already exists, inspect it before replacing it.

## Frontend Checks

Run from `apps/web/`:

```bash
pnpm lint-staged
pnpm lint
pnpm typecheck
```

## Backend Checks

Run from `apps/api/`:

```bash
.venv/bin/ruff format .
.venv/bin/ruff check .
```

## Notes

The hook is intentionally fast. Full builds and full test suites should run manually or in CI later.
