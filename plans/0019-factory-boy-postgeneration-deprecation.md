# Plan: Factory Boy Postgeneration Deprecation

## Status

Draft

## Linked Specs

- `CHANGELOG.md` (upgrade tracking)
- No product spec; test-infrastructure maintenance only.

## Objective

Remove the `factory-boy` `_after_postgeneration` deprecation that will stop
saving instances after post-generation hooks in the next major release. The
deprecation currently emits a warning on every factory-based test run and will
become an error on upgrade.

## Scope

In scope:

- Replace `factory.PostGenerationMethodCall` usage in `AccountFactory` with an
  explicit post-generation hook that saves explicitly.
- Verify the full API test suite still passes against PostgreSQL.

Out of scope:

- Upgrading `factory-boy` to 4.x (separate change; pin stays at `3.3.3`).
- Other factory_boy modernization.

## Dependencies

- Technical decisions: Keep the `factory_boy==3.3.3` pin. This task only makes
  the codebase forward-compatible so the 4.x upgrade is a dependency bump, not
  a code change.

## Phases

### Phase 1: Explicit Password Post-Generation

#### Task 1: Replace PostGenerationMethodCall in AccountFactory

Description: In
`apps/api/tests/recommendations/factories.py`, `AccountFactory.password` uses
`factory.PostGenerationMethodCall("set_password", "testpass123")`, which relies
on the deprecated implicit save after post-generation hooks. Replace it with a
`@factory.post_generation` method that hashes the password and calls
`obj.save()` explicitly when the strategy is `create` (preserving the raw value
for `build`/`build_batch` callers that need an un-hashed password).

Acceptance criteria:

- [ ] `AccountFactory` no longer uses `PostGenerationMethodCall`.
- [ ] `AccountFactory().check_password("testpass123")` is `True`.
- [ ] `AccountFactory.build()` exposes the raw password (existing build-path
      behavior preserved).
- [ ] No `_after_postgeneration` deprecation warning appears in test output.

Verification:

- [ ] Tests pass: `bash scripts/test-postgres.sh tests/ -q` (Docker running).
- [ ] Manual check: `pytest -W error::DeprecationWarning` on a factory usage
      shows no factory_boy deprecation.

Files likely touched:

- `apps/api/tests/recommendations/factories.py`

Dependencies: None.

Estimated scope: Small.

## Checkpoints

- [ ] After the task, the full API suite passes and the deprecation warning is
      gone from test output.
- [ ] Before completion, `CHANGELOG.md` records the forward-compatibility fix.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Build-strategy tests stop getting a raw password | Medium | Preserve the raw-value branch explicitly and cover it in verification. |
| Implicit saves elsewhere in factories | Low | Grep for `PostGenerationMethodCall` repo-wide; this is the only usage. |

## Open Questions

- None.