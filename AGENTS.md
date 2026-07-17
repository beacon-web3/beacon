# Agent Instructions

## Project Context

Beacon is a books-first decentralized discovery marketplace on Solana. Users
create canonical book recommendations by locking a curator stake, and other
users support those recommendations with small SOL contributions. The product
goal is to reward taste, early discovery, and public curation reputation.

Beacon must be framed as a discovery and reputation network, not as a passive
yield product, guaranteed-profit system, or investment return mechanism.

## Canonical Product Specs

Use these documents as the source of truth before designing or implementing
product behavior. Start with the OKF bundle index for a full navigation map:

- `docs/index.md` - OKF knowledge bundle index (full document listing).
- `docs/product/vision.md` - Long-term thesis, positioning, and principles.
- `docs/product/mvp.md` - Books-first MVP scope, exclusions, and open questions.
- `docs/product/user-stories.md` - User-facing behavior and acceptance criteria.
- `docs/product/governance.md` - Draft governance model and decision boundaries.
- `docs/product/treasury.md` - Treasury, operating reserve, and transparency model.
- `docs/product/risks.md` - Product, economic, trust, legal, and abuse risks.
- `docs/product/assumptions.md` - Draft assumptions and their review status.
- `docs/product/open-questions.md` - Unresolved questions agents must not invent answers for.
- `docs/product/roadmap.md` - Phase-based product and launch roadmap.
- `docs/tokenomics/rewards.md` - Draft support, milestone reward, and badge mechanics.
- `docs/tokenomics/staking.md` - Draft staking model for treasury and locked SOL.
- `docs/architecture/system-design.md` - System boundaries and architecture direction.
- `docs/decisions/` - Business, product, and technical decision records.
- `docs/plans/` - Implementation plans that break approved work into tasks.
- `CHANGELOG.md` - Meaningful project changes by date or release.

If implementation and documentation disagree, stop and surface the conflict
instead of silently choosing one interpretation.

## Product Guardrails

- Do not invent reward formulas, treasury splits, staking behavior, governance
  rules, badge mechanics, or revenue models outside the documented specs.
- Treat tokenomics, treasury allocation, staking, governance, and NFT badge
  parameters as draft assumptions until explicitly confirmed, simulated, legally
  reviewed, security-reviewed, or community-approved as appropriate.
- Do not add a governance token unless explicitly requested.
- Do not describe supporter payments as refundable votes; support represents
  conviction and may create badge, reputation, and milestone-reward eligibility.
- Do not imply that NFT badges represent ownership of books, book IP, or cover
  art. Badges represent Beacon participation and discovery history.
- Prefer conservative native SOL staking assumptions over DeFi yield strategies
  unless the user explicitly requests a different model.

## Repository Map

- `apps/web/` - Nuxt/Vue frontend.
- `apps/api/` - Django and Django REST Framework backend.
- `apps/contracts/` - Solana programs and contract workspace.
- `packages/sdk/` - Shared client SDK.
- `packages/types/` - Shared TypeScript types.
- `packages/config/` - Shared configuration.
- `docs/` - Product, architecture, tokenomics, and development documentation.

## Spec-Driven Workflow

For new features or behavior changes, consult or update the relevant product,
tokenomics, architecture, or API document before implementing. If requirements
are missing or ambiguous, ask a short clarifying question instead of inventing
product policy.

For multi-step features or changes, create or update a plan in `docs/plans/`
before implementation. Plans should link to relevant specs and decision records,
break work into small tasks, include acceptance criteria, list verification
steps, and identify blocked open questions. Do not implement tasks that depend
on unresolved product policy unless the user explicitly resolves the question.

## Documentation Maintenance

- Record significant business, product, technical, economic, governance,
  treasury, security, or architecture decisions in `docs/decisions/`.
- Update `docs/decisions/README.md` whenever adding or changing a decision
  record.
- Update `CHANGELOG.md` for meaningful product, documentation, architecture,
  API, contract, infrastructure, and launch changes. Do not log tiny mechanical
  edits.
- Add new unresolved product or policy questions to
  `docs/product/open-questions.md` rather than answering them implicitly.
- Add new draft economic, governance, staking, treasury, badge, or launch
  assumptions to `docs/product/assumptions.md` with the appropriate review
  status.
- If a changelog entry or decision record would be misleading without a related
  spec update, update the relevant spec in the same change.
- Keep `docs/plans/` current when implementing planned work: update task status,
  record scope changes, and mark completed plans only after verification.

Use the `using-agent-skills` skill when starting a session or when it is
unclear which skill applies. It covers skill discovery, domain-specific routing
(Vue/Nuxt, Django/Python, Solana/Web3, Frontend/UI), lifecycle sequencing, and
core operating behaviors. Skill rules and the full skill catalog live there —
this file does not duplicate them.

## Custom Agents

### Review Agent

Read-only code review agent. Reviews code without modifying files and outputs
a findings-only report.

- **Small diffs**: Reviews directly in-process, loading relevant domain skills.
- **Wide or multi-domain diffs**: Orchestrates specialist sub-agents in parallel
  (frontend, backend, web3) and consolidates findings into one report.
- **Modes**: `auto` (default, threshold-based routing), `direct`, `orchestrate`.
- **Scope**: Default reviews all uncommitted changes including staged, unstaged,
  and untracked files. Also supports `selected-files` and `branch-all` scopes.
- **Limits**: Max 100 files, max 5,000 diff lines. Warns and suggests narrowing
  if exceeded.
- **Config**: `.opencode/agents/review-agent.json`
- **Agent instructions**: `.opencode/agents/review-agent.md`
- **Human docs**: `docs/development/review-agent.md`

Invoke via OpenCode with `review-agent` or invoke the agent by name. Use
`--mode direct` or `--mode orchestrate` to override auto-routing.

### Lead Developer

Plan-driven implementation agent. Builds features across domains by reading
tasks from plans or standalone descriptions, with domain-specific validation
gates and parallel specialist orchestration.

- **Small single-domain tasks**: Implements directly in-process, loading
  relevant domain skills.
- **Multi-domain features**: Orchestrates specialist sub-agents in parallel
  (frontend, backend, web3, shared, documentation) with file ownership
  boundaries, and handles cross-domain integration itself.
- **Modes**: `auto` (default, threshold-based routing), `direct`, `orchestrate`.
- **Validation**: Pre-flight and post-flight checks per domain. Post-flight
  failures block subsequent tasks.
- **Limits**: Max 20 tasks per run. Warns and suggests splitting if exceeded.
- **Config**: `.opencode/agents/lead-developer.json`
- **Agent instructions**: `.opencode/agents/lead-developer.md`
- **Human docs**: `docs/development/lead-developer.md`

Invoke via OpenCode with `lead-developer` or invoke the agent by name. Use
`--mode direct` or `--mode orchestrate` to override auto-routing. Use
`--plan <filename>` to implement from a plan, or `--task "description"` for a
standalone task.

### Planner

Spec-aware planning agent. Reads product specs, decisions, assumptions, and
codebase context to produce structured implementation plans in `docs/plans/`.
Plans are consumable by the lead-developer agent via `--plan`.

- **Quick plan**: Light context gathering for simple, single-domain features.
  3-8 tasks.
- **Full plan**: Thorough context gathering with codebase exploration for
  complex, multi-domain features. Detailed task decomposition.
- **Modes**: `auto` (default, routes between quick and full plan), `direct`
  (always full plan).
- **Input**: Feature description, spec file paths, or product area scope.
- **Core skills**: spec-driven-development, planning-and-task-breakdown,
  context-engineering (always loaded).
- **Dynamic skills**: Domain-specific skills loaded based on feature scope.
- **Codebase exploration**: Explores existing patterns (models, views,
  components, contracts) before decomposing work.
- **Conflict detection**: Checks existing plans for overlapping scope.
- **Limits**: Max 20 tasks per plan. Warns and suggests splitting if exceeded.
- **Config**: `.opencode/agents/planner.json`
- **Agent instructions**: `.opencode/agents/planner.md`
- **Human docs**: `docs/development/planner.md`

Invoke via OpenCode with `planner` or invoke the agent by name. Use
`--description "feature description"` to plan from a description, or
`--scope "area"` to plan for a product area. Use `--dryRun` to preview without
writing.
