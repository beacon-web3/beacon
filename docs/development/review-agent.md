# Review Agent

> For the full agent prompt and behavioral logic (routing, specialist template,
> consolidation, scope resolution, analysis dimensions), see
> `.opencode/agents/review-agent.md`.

Read-only code review agent that prints a findings-only report. It never
modifies files, commits, or writes output beyond its final message.

## Quick Start

```
review-agent                                    # auto-route (default)
review-agent --mode direct                      # force inline review
review-agent --mode orchestrate                 # force specialist spawning
review-agent --scope branch-all                 # review branch vs default base
review-agent --scope selected-files --paths '["apps/web/components/"]'
```

## How It Works

The agent resolves a diff, classifies changed files by domain, and decides
whether to review directly or orchestrate specialist sub-agents.

### Routing (Auto Mode)

1. Collect the diff for the resolved scope.
2. Classify each file by domain (see Domain Map below).
3. Apply routing rules:

| Condition | Mode |
|---|---|
| `--mode direct` | Direct |
| `--mode orchestrate` | Orchestrate |
| Files ≤ `singleDomainThreshold` and one domain | Direct |
| Files ≤ `singleDomainThreshold` and multiple domains | Direct (all domain skills loaded) |
| Files > `singleDomainThreshold` or diff > `maxDiffLines` | Orchestrate |
| Files > `maxFiles` | Warn and stop |

Default threshold: 10 files. Cross-domain diffs always orchestrate regardless
of threshold when file count exceeds it.

### Direct Mode

The agent reviews code inline, loading the four core skills plus
domain-specific skills for every touched domain.

### Orchestrate Mode

The agent groups files by domain, spawns one specialist sub-agent per domain
via the `task` tool, and consolidates their findings into a single report.

Specialist sub-agents are spawned in parallel. Each specialist loads the four
core skills plus its domain-specific skills. Cross-domain issues (e.g., API
contract changes affecting both frontend and backend) are reviewed by the
orchestrator, not by specialists.

## Domain Map

| Path prefix | Domain | Key skills |
|---|---|---|
| `apps/web/` | Frontend | vue-best-practices, frontend-ui-engineering, nuxt, nuxt-ui, frontend-development-tailwind-design-system |
| `apps/api/` | Backend | django-backend-development, python-development-python-code-style, python-development-python-error-handling, database-design-postgresql |
| `apps/contracts/` | Web3 | solana-dev, blockchain-web3-solidity-security |
| `packages/` | Shared | Depends on package content |
| `docs/` | Documentation | documentation-and-adrs |
| Root config | Config | Match to the domain they configure |

### Backend Test Infrastructure

All Django tests requiring PostgreSQL run via `apps/api/scripts/test-postgres.sh`
(or `bash scripts/test-postgres.sh` from `apps/api/`). The script:

1. Checks Docker Desktop is running.
2. Starts PostgreSQL in Docker Compose (`docker compose up -d postgres`).
3. Waits for readiness (up to 30s via `pg_isready`).
4. Runs pytest with `DATABASE_URL` pointing at the Compose database.

When reviewing backend test changes, verify compatibility with this script:
- Fixtures must set all required model fields (the script does not patch them).
- No hardcoded database URLs outside the script.
- Tests that need the database are marked with `@pytest.mark.django_db`.

## Scopes

- **uncommitted** (default): All uncommitted changes — staged and unstaged modifications (`git diff HEAD`), plus untracked new files (read in full). Excludes `.gitignore`-matched files.
- **selected-files**: Restricts to provided paths or globs.
- **branch-all**: Compares current branch against the base branch.

### Base Branch Resolution

When `scope=branch-all` and `baseBranch=auto` (default):

1. Remote default branch via `git symbolic-ref refs/remotes/origin/HEAD`.
2. Local `main`, then local `master`.
3. Falls back to `HEAD` with a warning.

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| `mode` | `auto` \| `direct` \| `orchestrate` | `auto` | Review mode |
| `scope` | `uncommitted` \| `selected-files` \| `branch-all` | `uncommitted` | What to review |
| `paths` | `string[]` | `[]` | Files/globs when scope=selected-files |
| `baseBranch` | `string` | `auto` | Base branch for branch-wide review |
| `singleDomainThreshold` | `number` | `10` | Max files before orchestration kicks in |
| `maxFiles` | `number` | `100` | Hard cap on files reviewed |
| `maxDiffLines` | `number` | `5000` | Hard cap on total diff lines |
| `webSearch` | `boolean` | `true` | Allow web search for best-practice findings |
| `includeRiskyAreasBeyondDiff` | `boolean` | `true` | Consider risky areas beyond the diff |
| `alwaysLoadSkills` | `string[]` | (4 core skills) | Skills to always load |

## Core Skills (always loaded)

- `code-review-and-quality`
- `security-and-hardening`
- `performance-optimization`
- `code-simplification`

## Output Format

The report includes:

- **Scope**: what was reviewed and which specialists contributed (orchestrate mode).
- **Mode**: direct or orchestrate.
- **Selected Skills**: skills loaded and used.
- **Summary**: 1–3 sentence assessment.
- **Findings**: numbered list with severity, location (file:line), description,
  evidence, and suggested skill(s) for fixing.

## Error Handling

- No uncommitted changes: informs user, suggests switching to branch-wide scope.
- Invalid base branch: falls back to resolved default branch.
- Shallow clone: warns about limited branch-wide review.
- Binary files in diff: skipped, noted in report.
- Detached HEAD: warns, suggests checking out a branch.
- Merge conflicts: warns, continues with clean diffs.
