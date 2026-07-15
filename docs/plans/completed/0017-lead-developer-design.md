# Plan: Lead Developer Agent

## Status

Completed

## Linked Specs

- `docs/decisions/0020-review-agent-design.md` — Review agent pattern to follow
- `docs/decisions/0021-lead-developer-design.md` — This agent's ADR
- `docs/development/review-agent.md` — Parallel documentation pattern

## Objective

Add a plan-driven Lead Developer Agent to OpenCode that implements code across
Beacon's domains with domain-specific validation, parallel specialist
orchestration, and file ownership boundaries.

## Scope

In scope:

- Agent config (`.opencode/agents/lead-developer.json`).
- Agent behavioral instructions (`.opencode/agents/lead-developer.md`).
- Human-facing documentation (`docs/development/lead-developer.md`).
- ADR documenting the decision (`docs/decisions/0021-lead-developer-design.md`).
- AGENTS.md update documenting the new agent.

Out of scope:

- Actual domain-specific pre/post-flight commands (may need tuning after
  first real use).
- Specialist agent configs (specialists are spawned dynamically via `task`).

## Dependencies

- Product decisions: None (agent infrastructure only).
- Technical decisions: `0020-review-agent-design.md` (pattern reference).
- Open questions: None.

## Phases

### Task 1: Create agent config

Description: Create `.opencode/agents/lead-developer.json` with all agent
options (mode, plan, task, taskIndex, paths, baseBranch, alwaysLoadSkills,
dryRun, skipTests, singleDomainThreshold, maxTasks).

Acceptance criteria:

- [x] JSON is valid and parseable.
- [x] All options have type, default, and description.
- [x] Name is `lead-developer`.

Verification:

- [x] `cat .opencode/agents/lead-developer.json | python3 -m json.tool` passes.

Files likely touched:

- `.opencode/agents/lead-developer.json`

Dependencies: None.

Estimated scope: Small.

### Task 2: Create agent instructions

Description: Create `.opencode/agents/lead-developer.md` with full behavioral
logic covering routing, direct mode, orchestrate mode, domain mapping, file
ownership, pre/post-flight checks, dynamic skill loading, error recovery,
output format, and verification.

Acceptance criteria:

- [x] All sections from the design are covered.
- [x] Domain mapping matches review-agent's path-prefix convention.
- [x] File ownership table is complete for all 5 domains + orchestrator.
- [x] Pre-flight and post-flight commands are specified per domain.
- [x] Dynamic skill loading table covers all identified task signals.

Verification:

- [x] File is well-formed markdown with consistent heading hierarchy.
- [x] Cross-references to human docs and ADR are present.

Files likely touched:

- `.opencode/agents/lead-developer.md`

Dependencies: Task 1.

Estimated scope: Large.

### Task 3: Create human documentation

Description: Create `docs/development/lead-developer.md` with quick start
examples, how it works summary, domain map, options reference, pre/post-flight
check details, and error handling.

Acceptance criteria:

- [x] Quick start examples cover plan, standalone task, mode override, and
  dry run.
- [x] Options table matches the JSON config.
- [x] Domain map and dynamic skill loading are documented.

Verification:

- [x] File follows the same structure as `docs/development/review-agent.md`.

Files likely touched:

- `docs/development/lead-developer.md`

Dependencies: Task 2.

Estimated scope: Medium.

### Task 4: Create ADR

Description: Create `docs/decisions/0021-lead-developer-design.md` documenting
the decision, alternatives considered, and consequences.

Acceptance criteria:

- [x] Status is Accepted.
- [x] All alternatives from the design are documented.
- [x] Links to agent config, instructions, and human docs are present.

Verification:

- [x] File follows the ADR format from `0020-review-agent-design.md`.

Files likely touched:

- `docs/decisions/0021-lead-developer-design.md`

Dependencies: Task 2.

Estimated scope: Small.

### Task 5: Update AGENTS.md

Description: Add Lead Developer Agent entry to the Custom Agents section in
`AGENTS.md`, following the same format as the Review Agent entry.

Acceptance criteria:

- [x] Entry includes name, description, modes, config path, instructions path,
  and human docs path.
- [x] Entry is placed after the Review Agent entry.

Verification:

- [x] `AGENTS.md` renders correctly with both agent entries.

Files likely touched:

- `AGENTS.md`

Dependencies: Task 2.

Estimated scope: Small.

### Task 6: Update index files

Description: Update `docs/decisions/README.md` index with the new ADR, update
`docs/plans/README.md` active plans table, and add a changelog entry to
`CHANGELOG.md`.

Acceptance criteria:

- [x] `docs/decisions/README.md` has row for 0021.
- [x] `docs/plans/README.md` has row for 0017 with Completed status.
- [x] `CHANGELOG.md` has an entry under Unreleased > Added.

Verification:

- [x] All three index files are consistent.

Files likely touched:

- `docs/decisions/README.md`
- `docs/plans/README.md`
- `CHANGELOG.md`

Dependencies: Tasks 4, 5.

Estimated scope: Small.

## Checkpoints

- [x] After Tasks 1-2: Agent config and instructions are complete and
  internally consistent.
- [x] After Tasks 3-5: Documentation, ADR, and AGENTS.md are complete.
- [x] After Task 6: All index files and changelog are updated.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Pre/post-flight commands may not match actual project tooling | Low | Commands are conservative defaults; can be tuned after first real use |
| Agent instructions may drift from review-agent conventions | Low | Both agents follow the same structural pattern; cross-referenced in ADR |

## Open Questions

- None. All design decisions were resolved during the planning session.
