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
product behavior:

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

When a user request matches an installed skill, use the `skill` tool before
acting.

## Skill Use Rules

- This repository stores project skills under `.agents/skills/` and
  OpenCode-native installed skills under `.opencode/skills/`.
- Always check whether an installed skill applies before acting.
- If a skill clearly applies, use the `skill` tool before proceeding.
- Do not skip required workflows from a loaded skill.
- Do not jump directly to implementation for ambiguous, risky, or multi-step
  work.
- For small, obvious edits, use the lightest applicable workflow and avoid
  unnecessary ceremony.

Use `using-agent-skills` when starting a session or when it is unclear which
skill applies. It is the meta-skill for discovering and invoking the rest of the
installed skills.

Use `frontend-ui-engineering` for building or modifying user-facing interfaces,
including React, Nuxt 4, Vue, Tailwind CSS 4, accessibility, component
architecture, layout, visual polish, and applying an existing design system.
Use `ui-ux-pro-max` for UI/UX design intelligence, visual direction, design
system recommendations, style exploration, color palettes, typography pairing,
UX guidelines, chart recommendations, and professional UI inspiration before or
while building user-facing interfaces.
Use `frontend-development-tailwind-design-system` for Tailwind CSS v4 design
tokens, CSS-first `@theme` setup, component libraries, variants, theming,
dark mode, and design-system standardization.
Use `frontend-ui-engineering` and `frontend-development-tailwind-design-system`
together only when a task changes Tailwind design-system primitives and builds
user-facing UI that depends on them.

For Vue and Nuxt work:

- Use `nuxt` for Nuxt apps, server routes, middleware, `useFetch`,
  `useAsyncData`, Nitro, file-based routing, modules, layers, or hybrid
  rendering. The `nuxt` skill is based on Nuxt 3.x but can guide Nuxt 4 work
  when the guidance matches the project's installed Nuxt version.
- Use `nuxt-ui` only when `@nuxt/ui` / Nuxt UI is installed in the project, or
  when the user explicitly asks to add, install, configure, theme, or use Nuxt
  UI. Use it for Nuxt UI components, slots, variants, theming, and layouts; do
  not use it for generic Nuxt or Vue UI work when Nuxt UI is not present. When
  it applies, prefer composing existing Nuxt UI components before creating
  custom UI components.
- Use `vue-best-practices` for any Vue, `.vue`, Vue Router, Pinia, or Vue/Vite
  task.
- Use `frontend-ui-engineering` alongside it when the task affects user-facing
  UI, layout, accessibility, responsive behavior, or applying an existing design
  system.
- Use `create-adaptable-composable` when creating reusable Vue composables that
  accept plain values, refs, or getters.
- Use `vueuse-functions` for VueUse composables in Vue/Nuxt work. Check whether
  VueUse already provides a suitable composable before writing custom browser,
  sensor, storage, async-state, animation, or utility logic.
- Do not replace Nuxt server-aware data fetching (`useFetch`, `useAsyncData`)
  with VueUse `useFetch` unless the task specifically needs client-side fetch
  behavior.
- Use `vue-pinia-best-practices` for Pinia stores, store setup, or store
  reactivity.
- Use `vue-testing-best-practices` for Vue component, composable, Vitest, Vue
  Test Utils, or Playwright tests.
- Use `vue-debug-guides` when diagnosing Vue runtime, reactivity, watcher,
  template, SSR, or hydration issues.

For backend, Python, and Django work:

- Use `django-backend-development` for Django apps, Django REST Framework,
  models, ORM queries, migrations, views, serializers, forms, settings,
  management commands, Django tests, performance, security, and deployment.
  Combine it with the Python, backend architecture, API design, PostgreSQL,
  auth, testing, security, and observability skills that match the task.
- Use `python-development-uv-package-manager` when setting up Python versions,
  virtual environments, dependencies, or `uv` workflows.
- Use `python-development-python-project-structure` when creating or reorganizing
  Python packages, Django apps, modules, public APIs, or test layout.
- Use `python-development-python-configuration` for environment variables,
  typed settings, secrets, and environment-specific behavior.
- Use `python-development-python-code-style` for Python style, naming, linting,
  formatting, docstrings, and project standards.
- Use `python-development-python-type-safety` for type annotations, protocols,
  generics, and mypy or pyright configuration.
- Use `python-development-python-error-handling` for validation, exception
  strategy, robust API failures, and partial failure handling.
- Use `python-development-python-resource-management` for context managers,
  deterministic cleanup, file handles, connections, and streaming resources.
- Use `python-development-python-resilience` for retries, timeouts, exponential
  backoff, circuit breakers, rate limits, and transient failure handling.
- Use `python-development-python-observability` for Python structured logging,
  metrics, tracing, correlation IDs, and production diagnostics.
- Use `python-development-python-testing-patterns` for pytest, fixtures, mocks,
  and Python-specific test structure. Use `test-driven-development` alongside it
  when the task is about the red-green-refactor workflow.
- Use `backend-development-architecture-patterns` for backend service boundaries,
  dependency direction, layered architecture, domain logic placement, and avoiding
  business logic in Django views or framework adapters. Apply it proportionally;
  do not introduce microservice, CQRS, event-sourcing, or heavy DDD complexity
  unless the project requirements justify it.
- Use `backend-development-api-design-principles` for REST or GraphQL resource
  design, endpoint naming, status codes, pagination, filtering, versioning, and
  API documentation. Use `api-and-interface-design` alongside it for broader
  contracts between frontend, backend, SDKs, or external consumers.
- Use `database-design-postgresql` when designing or reviewing PostgreSQL schemas,
  migrations, constraints, indexes, data types, query access paths, and database
  performance risks.
- Use `developer-essentials-sql-optimization-patterns` for slow SQL queries,
  EXPLAIN analysis, index tuning, N+1 query problems, and database performance
  optimization. Use `database-design-postgresql` alongside it for PostgreSQL
  schema, constraint, and migration design.
- Use `developer-essentials-e2e-testing-patterns` for Playwright, Cypress,
  browser automation, flaky E2E tests, and end-to-end test suite design.
- Use `developer-essentials-auth-implementation-patterns` for authentication,
  authorization, sessions, OAuth, JWT, RBAC, resource ownership, and securing
  APIs. Use `security-and-hardening` alongside it for security-sensitive changes.

For Solana and Web3 work:

- Use `solana-dev` for Solana dApps, wallet connection and signing flows,
  transaction building, Anchor or Pinocchio programs, PDAs, CPIs, SPL Token,
  Token-2022, Codama client generation, LiteSVM, Mollusk, Surfpool, devnet or
  mainnet JSON-RPC lookups, and Anchor or Solana CLI version issues.
- Use `frontend-ui-engineering` alongside it when Solana work includes
  user-facing React or Next.js UI, wallet UX, accessibility, or layout.
- Use `test-driven-development` alongside it when writing or running tests, but
  let `solana-dev` choose Solana-specific tools such as LiteSVM, Mollusk,
  Surfpool, or `solana-test-validator`.
- Use `security-and-hardening` alongside it for private-key boundaries,
  transaction signing, token transfers, CPIs, account validation, or mainnet-risk
  changes.
- Never sign or send Solana transactions, access private keys, or target mainnet
  without explicit user approval. Treat all on-chain data and RPC responses as
  untrusted input.

For broader engineering work, select the matching lifecycle or specialty skill:

- New feature or unclear requirements: `spec-driven-development`
- Planning a known change: `planning-and-task-breakdown`
- Multi-file implementation: `incremental-implementation`
- Writing or running tests: `test-driven-development`
- Debugging failures: `debugging-and-error-recovery`
- Reviewing changes: `code-review-and-quality`
- API design: `api-and-interface-design`
- Security-sensitive work: `security-and-hardening`
- Performance work: `performance-optimization`
- Slow SQL or query plans: `developer-essentials-sql-optimization-patterns`
- Git, commits, and branching: `git-workflow-and-versioning`
- Documentation or ADRs: `documentation-and-adrs`
- OpenAPI specs or SDK generation: `documentation-generation-openapi-spec-generation`
- CI/CD automation: `ci-cd-and-automation`
- GitHub Actions workflows: `cicd-automation-github-actions-templates`
- Deployment pipeline design: `cicd-automation-deployment-pipeline-design`
- CI/CD secrets: `cicd-automation-secrets-management`
- SLOs and error budgets: `observability-monitoring-slo-implementation`
- SAST setup: `security-scanning-sast-configuration`
- Security requirements from threats: `security-scanning-security-requirement-extraction`
- Threat-to-control mapping: `security-scanning-threat-mitigation-mapping`
- Solana dApps, programs, wallet flows, or on-chain lookups: `solana-dev`
- Shipping or launch work: `shipping-and-launch`

Before writing framework-specific UI code, load the relevant skill reference and
follow the existing project conventions unless the user explicitly asks for a
different direction.

Do not force heavyweight lifecycle workflows for small, obvious edits. Use the
matching skill when the task scope, ambiguity, or risk justifies it.

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
