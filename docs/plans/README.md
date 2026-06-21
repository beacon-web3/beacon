# Implementation Plans

This directory tracks implementation plans for multi-step Beacon work.

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

## Index

| ID | Plan | Status |
| --- | --- | --- |
| 0001 | [Documentation foundation](0001-documentation-foundation.md) | Completed |
| 0002 | [Frontend design system foundation](0002-frontend-design-system.md) | Completed |
| 0003 | [Homepage clarity and French localization](0003-homepage-clarity-localization.md) | Completed |
| 0004 | [Auth entry UI refresh](0004-auth-entry-ui-refresh.md) | Completed |
