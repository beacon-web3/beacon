# Planner Agent

> For the full agent prompt and behavioral logic (context gathering, codebase
> exploration, conflict detection, task decomposition, dynamic skill loading),
> see `.opencode/agents/planner.md`.

Spec-aware planning agent that reads product specs, decisions, assumptions, and
codebase context to produce structured implementation plans in `docs/plans/`.
Plans are consumable by the lead-developer agent via `--plan`.

## Quick Start

```
planner --description "Add a bookmark feature for curators"          # plan from description
planner --scope "governance"                                         # plan for a product area
planner --specs "docs/product/user-stories.md" "docs/tokenomics/rewards.md"  # plan from specific specs
planner --description "..." --dryRun                                 # preview plan without writing
planner --description "..." --mode direct                            # force full plan
planner --description "..." --outputPath docs/plans/0023-bookmarks.md  # custom output path
```

## How It Works

The agent gathers context from product specs, decisions, assumptions, and the
codebase, then decomposes the feature into verifiable tasks.

### Routing (Auto Mode)

1. Resolve input (description, specs, scope).
2. Classify complexity (quick vs full plan).
3. Apply routing rules:

| Condition | Mode |
|---|---|
| `--mode direct` | Full plan |
| Single domain, clear scope | Quick plan |
| Multiple domains | Full plan |
| Cross-cutting concerns | Full plan |
| More than 2 spec files | Full plan |
| Vague description | Full plan |

### Quick Plan Mode

Light context gathering. 3-8 tasks. Suitable for simple, single-domain
features.

### Full Plan Mode

Thorough context gathering with codebase exploration. Detailed task
decomposition. Suitable for complex features.

## Context Sources

The agent reads from:

- **Product specs** in `docs/product/` — vision, MVP, user stories, risks,
  assumptions, open questions, roadmap.
- **Tokenomics** in `docs/tokenomics/` — rewards, staking mechanics.
- **Architecture** in `docs/architecture/` — system design, boundaries.
- **Decisions** in `docs/decisions/` — past business, product, technical
  decisions.
- **Codebase patterns** — existing models, views, components, contracts,
  tests.

## Codebase Exploration

In full plan mode, the agent explores the codebase to understand existing
patterns:

- Django models, views, serializers (`apps/api/`)
- Vue components, composables, stores (`apps/web/`)
- Solana programs (`apps/contracts/`)
- Shared packages (`packages/`)
- Test patterns and conventions

This ensures the plan follows existing conventions and identifies reuse
opportunities.

## Conflict Detection

The agent checks existing plans in `docs/plans/` for overlapping scope and
flags conflicts or dependencies in the output plan.

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| `mode` | `auto` \| `direct` | `auto` | Quick or full plan |
| `description` | `string` | — | Feature description to plan |
| `specs` | `string[]` | `[]` | Paths to specific spec files |
| `scope` | `string` | — | Broad product area |
| `paths` | `string[]` | `[]` | Restrict codebase exploration |
| `baseBranch` | `string` | `auto` | Base branch for conflict detection |
| `outputPath` | `string` | `auto` | Where to write the plan file |
| `dryRun` | `boolean` | `false` | Preview plan without writing |
| `maxTasks` | `number` | `20` | Max tasks per plan |
| `alwaysLoadSkills` | `string[]` | (3 core skills) | Core skills to always load |

## Core Skills (always loaded)

- `spec-driven-development` — methodology for grounding plans in specs
- `planning-and-task-breakdown` — methodology for decomposing work
- `context-engineering` — methodology for understanding codebase context

## Dynamic Skill Loading

Domain-specific skills are loaded when the feature clearly touches that area:

| Feature area | Skills loaded |
|---|---|
| Frontend/UI | frontend-ui-engineering, vue-best-practices |
| Nuxt | nuxt, nuxt-ui |
| Tailwind | frontend-development-tailwind-design-system |
| Django/backend | django-backend-development |
| Database | database-design-postgresql |
| API design | api-and-interface-design |
| Solana/web3 | solana-dev |
| Security | security-and-hardening |
| Testing | test-driven-development |

## Output Format

The plan summary includes:

- **Mode**: quick or full.
- **Plan Written**: path to the plan file (or "dry run").
- **Skills Loaded**: all skills used.
- **Phases**: count and names.
- **Tasks**: count with scope breakdown.
- **Open Questions**: unresolved items.
- **Conflicts**: conflicts with existing plans.
- **Next Steps**: suggested `lead-developer --plan` invocation.

## Integration with Lead Developer

Plans produced by the planner agent are directly consumable by the
lead-developer agent:

```
lead-developer --plan docs/plans/0023-bookmarks.md
```

The lead-developer reads the plan, validates it, and implements tasks
sequentially with domain-specific validation gates.

## Error Handling

- Missing or ambiguous specs: flagged as open questions, not invented.
- Conflicts with existing plans: noted in the plan under risks or dependencies.
- Plan exceeds maxTasks: warns user and suggests splitting.
- No input provided: checks open questions or asks the user.
