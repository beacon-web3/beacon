# 0022 — Planner Agent Design

Status: Accepted
Date: 2026-07-15

## Context

The project has a lead-developer agent that implements plans and a review-agent
that reviews code, but there was no agent to produce the plans themselves.
Planning was done manually or by ad-hoc agent prompts during conversations. This
led to inconsistent plan quality, missing context gathering, and no systematic
codebase exploration before task decomposition. A dedicated planner agent
formalizes the planning step and produces plans that the lead-developer can
directly consume via `--plan`.

## Decision

Add a spec-aware Planner Agent with the following design:

- **Named `planner`** to clearly convey its purpose.
- **Two modes**: Auto mode routes between quick plan (light context gathering)
  and full plan (thorough exploration) based on input complexity. Direct mode
  always produces a full plan. No orchestrate mode — planning is inherently a
  single-domain activity.
- **Multi-source input**: Accepts feature descriptions, spec file paths, and
  product area scope. Synthesizes all available context.
- **Three core skills always loaded**: spec-driven-development (grounding in
  specs), planning-and-task-breakdown (task decomposition methodology),
  context-engineering (codebase understanding).
- **Dynamic domain skill loading**: Loads domain-specific skills when the
  feature touches frontend, backend, web3, or other domains.
- **Full codebase awareness**: Explores existing patterns (models, views,
  components, contracts) to ensure plans follow conventions and identify reuse.
- **Conflict detection**: Checks existing plans in `docs/plans/` for overlapping
  scope and flags dependencies or conflicts.
- **Output**: Structured plan file in `docs/plans/` following the existing
  template, consumable by lead-developer via `--plan`.
- **Dual documentation**: Agent instructions
  (`.opencode/agents/planner.md`) are the source of truth for agent behavior.
  Human docs (`docs/development/planner.md`) cover usage, CLI examples, and
  configuration reference.

## Alternatives Considered

- **Manual planning by humans**: Rejected because it's slow, inconsistent, and
  doesn't systematically explore the codebase. A dedicated agent automates the
  context gathering and decomposition.
- **Planning as part of lead-developer**: Rejected because it conflates planning
  and implementation. Separating concerns allows the planner to focus on
  context gathering and decomposition while the lead-developer focuses on
  execution and validation.
- **Orchestrate mode for planning**: Rejected because planning is inherently
  single-domain — it reads context and produces a document. There's no
  parallelization benefit from specialist sub-agents.
- **Always loading all domain skills**: Rejected because it wastes context
  tokens. The three core skills define the planning methodology; domain skills
  are loaded dynamically based on feature scope.
- **Planning without codebase exploration**: Rejected because plans that ignore
  existing patterns produce poor task decomposition and miss reuse
  opportunities.

## Consequences

- Plans become more consistent and thorough, with systematic context gathering
  from specs, decisions, and codebase patterns.
- The three core skills ensure methodology is always applied, not just for
  complex features.
- Dynamic skill loading keeps the planner's context lean for simple features
  while providing deep domain knowledge for complex ones.
- Conflict detection prevents duplicate or conflicting plans.
- The lead-developer agent benefits from higher-quality input plans.
- Adding a third agent increases the maintenance surface, but the consistent
  two-file pattern (config + instructions) and shared documentation structure
  keep it manageable.

## Links

- Agent config: `.opencode/agents/planner.json`
- Agent instructions: `.opencode/agents/planner.md`
- Human docs: `docs/development/planner.md`
- Review agent (parallel design): `docs/decisions/0020-review-agent-design.md`
- Lead developer (parallel design): `docs/decisions/0021-lead-developer-design.md`
- AGENTS.md: Custom Agents section
