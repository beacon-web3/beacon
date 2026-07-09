# Plan: Documentation Foundation

## Status

Completed

## Linked Specs

- `README.md`
- `AGENTS.md`
- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/governance.md`
- `docs/product/treasury.md`
- `docs/product/risks.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/product/roadmap.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/decisions/README.md`
- `CHANGELOG.md`

## Objective

Create the documentation structure needed for spec-driven Beacon development,
including product specs, decision records, assumptions, open questions, roadmap,
changelog, and agent-maintenance rules.

## Scope

In scope:

- Capture the books-first Beacon product thesis and MVP boundaries.
- Add governance, treasury, risk, tokenomics, and staking documentation.
- Add decision records for major product and economic choices.
- Add assumption, open-question, roadmap, changelog, and implementation-plan
  tracking.
- Update `AGENTS.md` so future agents maintain these files.

Out of scope:

- Implementing application code.
- Finalizing tokenomics, legal policy, staking providers, or governance rules.
- Deploying Solana programs or production infrastructure.

## Tasks

### Task 1: Product And Tokenomics Docs

Description: Update the core product and economic documentation from the Beacon
strategy discussion.

Acceptance criteria:

- [x] Product vision and books-first MVP are documented.
- [x] User stories capture curator, supporter, treasury, and governance behavior.
- [x] Rewards and staking are documented as draft assumptions where appropriate.

Verification:

- [x] Documentation files exist under `docs/product/` and `docs/tokenomics/`.
- [x] Product guardrails avoid yield-product or guaranteed-return framing.

Dependencies: None.

Estimated scope: Medium.

### Task 2: Decision And Governance Tracking

Description: Add records for important product, business, treasury, governance,
and staking decisions.

Acceptance criteria:

- [x] `docs/decisions/README.md` exists with an index.
- [x] Initial decision records exist for major launch assumptions.
- [x] Proposed decisions are not mislabeled as accepted.

Verification:

- [x] Decision record index links to every seeded decision record.

Dependencies: Task 1.

Estimated scope: Medium.

### Task 3: Assumptions, Open Questions, Roadmap, And Changelog

Description: Add support files that prevent agents from silently inventing
policy during implementation.

Acceptance criteria:

- [x] `docs/product/assumptions.md` tracks draft and accepted assumptions.
- [x] `docs/product/open-questions.md` centralizes unresolved questions.
- [x] `docs/product/roadmap.md` defines phase-based work.
- [x] `CHANGELOG.md` records meaningful documentation changes.

Verification:

- [x] New docs are linked from `README.md` and `AGENTS.md`.

Dependencies: Task 1.

Estimated scope: Medium.

### Task 4: Plan Tracking

Description: Add the implementation-plan directory, template, and maintenance
rules for future feature breakdowns.

Acceptance criteria:

- [x] `docs/plans/README.md` explains when and how to create plans.
- [x] `docs/plans/templates/feature-plan.md` provides a reusable template.
- [x] This plan records the documentation-foundation work.
- [x] `AGENTS.md`, `README.md`, and `CHANGELOG.md` reference plan tracking.

Verification:

- [x] `git diff --check` passes for documentation changes.

Dependencies: Tasks 1, 2, and 3.

Estimated scope: Small.

## Checkpoints

- [x] Product docs exist before decision and assumption tracking.
- [x] Decision records and assumptions are added before agent rules require them.
- [x] Plan tracking is added after the initial documentation foundation exists.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Docs become duplicated or inconsistent | High | Keep `AGENTS.md` as a map and guardrail file, not a full spec replacement. |
| Draft economics are treated as final | High | Track draft values in `docs/product/assumptions.md` and mark proposed decisions clearly. |
| Plans become stale | Medium | Require plan updates when scope changes and changelog updates on meaningful completion. |

## Open Questions

- Should future implementation plans require explicit human approval before agents
  start coding, or only for high-risk changes?
