# Lead Developer Agent

> For the full agent prompt and behavioral logic (routing, specialist template,
> file ownership, pre/post-flight checks, skill loading), see
> `.opencode/agents/lead-developer.md`.

Plan-driven implementation agent that builds Beacon features across domains. It
reads tasks from plans in `docs/plans/` or from standalone task descriptions,
implements them with domain-specific validation, and produces an implementation
report.

## Quick Start

```
lead-developer --plan 0016-recommendation-lifecycle-data-model.md           # implement all tasks from plan
lead-developer --plan 0016-recommendation-lifecycle-data-model.md --taskIndex 2  # implement task #3 only
lead-developer --task "Add a composable for wallet balance fetching"        # standalone task
lead-developer --mode direct --plan 0016-...                                # force direct mode
lead-developer --mode orchestrate --plan 0016-...                           # force specialist spawning
lead-developer --plan 0016-... --dryRun                                     # show plan without changes
```

## How It Works

The agent resolves input (plan file or task description), classifies tasks by
domain, and decides whether to implement directly or orchestrate specialist
sub-agents.

### Routing (Auto Mode)

1. Resolve input (plan tasks or standalone task).
2. Classify each task by domain (see Domain Map below).
3. Apply routing rules:

| Condition | Mode |
|---|---|
| `--mode direct` | Direct |
| `--mode orchestrate` | Orchestrate |
| All tasks in one domain and ≤ `singleDomainThreshold` | Direct |
| Tasks span 2+ domains | Orchestrate |
| Tasks > `singleDomainThreshold` in one domain | Orchestrate |
| Tasks > `maxTasks` | Warn and stop |

Default threshold: 5 tasks.

### Direct Mode

The agent implements tasks inline, loading the three core skills plus
domain-specific core skills. Each task goes through pre-flight, implementation,
and post-flight checks.

### Orchestrate Mode

The agent groups tasks by domain, spawns one specialist sub-agent per domain
via the `task` tool, and handles cross-domain tasks itself. Specialists run in
parallel.

## Domain Map

| Path prefix | Domain | Core skills | Dynamic skills |
|---|---|---|---|
| `apps/web/` | Frontend | vue-best-practices, frontend-ui-engineering | nuxt, nuxt-ui, vueuse-functions, vue-pinia-best-practices, frontend-development-tailwind-design-system |
| `apps/api/` | Backend | django-backend-development, python-development-python-code-style | database-design-postgresql, python-development-python-testing-patterns, python-development-python-error-handling |
| `apps/contracts/` | Web3 | solana-dev | security-and-hardening, blockchain-web3-solidity-security |
| `packages/` | Shared | Chosen dynamically per package | — |
| `docs/` | Documentation | documentation-and-adrs | — |

### Dynamic Skill Loading

Specialists load additional skills only when a task clearly signals the need:

| Task signal | Skill to load |
|---|---|
| "Add Pinia store" | vue-pinia-best-practices |
| "Use VueUse composable" | vueuse-functions |
| "Update Tailwind theme" | frontend-development-tailwind-design-system |
| "Add Nuxt UI components" | nuxt-ui |
| "Add database migration" | database-design-postgresql |
| "Add tests" | python-development-python-testing-patterns |
| "Error handling changes" | python-development-python-error-handling |
| "Security-sensitive" | security-and-hardening |
| "Add logging / metrics" | observability-and-instrumentation |

## File Ownership (Orchestrate Mode)

To prevent merge conflicts between parallel specialists:

| Domain | Owns | May Read |
|---|---|---|
| Frontend | `apps/web/**` | `packages/**`, `apps/api/**` |
| Backend | `apps/api/**` | `packages/**` |
| Web3 | `apps/contracts/**` | `packages/**` |
| Shared | `packages/{specific-package}/**` | — |
| Docs | `docs/**` | — |
| Orchestrator | Root configs, integration | All |

## Pre-flight and Post-flight Checks

### Pre-flight (before each task)

| Domain | Commands |
|---|---|
| All | `git status` (clean workspace check) |
| Frontend | `npx nuxi typecheck` |
| Backend | `ruff check .`, `python manage.py makemigrations --check --dry-run` |
| Web3 | `cargo check` |
| Shared | Package-specific lint/type check |

### Post-flight (after each task)

| Domain | Commands |
|---|---|
| Frontend | `npx nuxi typecheck`, `npm run lint` |
| Backend | `ruff check .`, `python manage.py test`, `python manage.py makemigrations --check` |
| Web3 | `cargo check`, `cargo test` |
| Shared | Package-specific lint + type check |
| All | `git diff --stat` |

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| `mode` | `auto` \| `direct` \| `orchestrate` | `auto` | Build mode |
| `plan` | `string` | — | Plan file in `docs/plans/` |
| `task` | `string` | — | Standalone task description |
| `taskIndex` | `number` | — | Zero-based index of specific task in plan |
| `paths` | `string[]` | `[]` | Restrict to specific files/dirs |
| `baseBranch` | `string` | `auto` | Base branch for post-implementation diff |
| `dryRun` | `boolean` | `false` | Show plan without modifying files |
| `skipTests` | `boolean` | `false` | Skip test execution in post-flight |
| `singleDomainThreshold` | `number` | `5` | Max tasks before orchestration |
| `maxTasks` | `number` | `20` | Hard cap on tasks per run |
| `alwaysLoadSkills` | `string[]` | (3 core skills) | Core skills to always load |

## Core Skills (always loaded)

- `incremental-implementation`
- `test-driven-development`
- `security-and-hardening`

## Output Format

The implementation report includes:

- **Plan**: which plan was implemented (or "standalone task").
- **Mode**: direct or orchestrate (list specialists, if orchestrate).
- **Skills Loaded**: all skills used.
- **Tasks Implemented**: numbered list with status, files changed, pre/post-flight
  results, and notes.
- **Integration Notes**: cross-domain concerns (orchestrate mode only).
- **Next Steps**: suggested follow-up actions.

## Error Handling

- Pre-flight failure: reports blocker, does not implement.
- Implementation failure: rolls back changes, reports error, continues if
  isolated.
- Post-flight failure: attempts straightforward fix; rolls back if not obvious.
- Specialist crash: reports failure, offers retry.
- Never silently skips a failed task.
