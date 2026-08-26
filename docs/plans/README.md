# Implementation Plans

This directory tracks implementation plans for multistep Beacon work.

Plans translate approved specs and decisions into small, verifiable tasks. They
are not product specs and should not introduce product policy that is missing
from the canonical documentation.

## When To Create A Plan

Create or update a plan when work:

- Touches multiple files or subsystems.
- Implements a user-facing feature or behavior change.
- Changes APIs, contracts, database schemas, treasury logic, tokenomics, staking,
  governance, or security-sensitive flows.
- Needs multiple implementation sessions or could be parallelized.

Small mechanical edits do not need a plan.

## Plan Lifecycle

Use these statuses:

- `Draft`: Proposed task breakdown, not approved for implementation.
- `Approved`: Ready to implement.
- `In Progress`: Implementation has started.
- `Completed`: Tasks and verification are complete.
- `Superseded`: Replaced by another plan.
- `Cancelled`: No longer intended.

## File Naming

Use sequential filenames:

```text
0001-documentation-foundation.md
0002-book-recommendation-mvp.md
0003-wallet-connection.md
```

Templates live in `docs/plans/templates/`.

## Maintenance Rules

- Link each plan to relevant specs, decision records, assumptions, and open
  questions.
- Break work into small tasks with acceptance criteria and verification steps.
- Mark blocked tasks clearly instead of inventing missing requirements.
- Update a plan when scope changes during implementation.
- Update `CHANGELOG.md` when a completed plan produces meaningful project
  changes.
- Move completed plan files into `docs/plans/completed/` and keep active,
  draft, in-progress, superseded, or canceled plans at the top level unless the
  archive structure changes.

## Active Plans

| ID   | Plan | Status    |
|------| --- |-----------|
| 0018 | [Recommendation lifecycle API](0018-recommendation-lifecycle-api.md) | Draft |

## Completed Plans

Completed plans are archived in `docs/plans/completed/` to keep active planning
easy to scan while preserving implementation history.

| ID   | Plan | Status    |
|------| --- |-----------|
| 0001 | [Documentation foundation](completed/0001-documentation-foundation.md) | Completed |
| 0002 | [Frontend design system foundation](completed/0002-frontend-design-system.md) | Completed |
| 0003 | [Homepage clarity and French localization](completed/0003-homepage-clarity-localization.md) | Completed |
| 0004 | [Auth entry UI refresh](completed/0004-auth-entry-ui-refresh.md) | Completed |
| 0005 | [Password auth and profile foundation](completed/0005-password-auth-and-profile-foundation.md) | Completed |
| 0006 | [Email verification OTP](completed/0006-email-verification-otp.md) | Completed |
| 0007 | [Backend auth hardening](completed/0007-backend-auth-hardening.md) | Completed |
| 0008 | [Auth error handling improvements](completed/0008-auth-error-handling.md) | Completed |
| 0009 | [Backend Localization](completed/0009-backend-localization.md) | Completed |
| 0010 | [Auth test split](completed/0010-auth-api-test-split.md) | Completed |
| 0011 | [Library upgrade plan](completed/0011-library-upgrade-plan.md) | Completed |
| 0012 | [Runtime Toolchain Upgrade Plan](completed/0012-runtime-toolchain-upgrade-plan.md) | Completed |
| 0013 | [Google Social Auth](completed/0013-google-social-auth.md) | Completed |
| 0014 | [Backend Swagger OpenAPI Docs](completed/0014-backend-swagger-openapi.md) | Completed |
| 0015 | [MVP free hosting setup](completed/0015-mvp-free-hosting-setup.md) | Completed |
| 0016 | [Recommendation lifecycle data model](completed/0016-recommendation-lifecycle-data-model.md) | Completed |
| 0017 | [Lead developer agent](completed/0017-lead-developer-design.md) | Completed |
