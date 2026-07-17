---
name: using-agent-skills
description: Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.
---

# Using Agent Skills

## Overview

Agent Skills is a collection of engineering workflow skills organized by development phase. Each skill encodes a specific process that senior engineers follow. This meta-skill helps you discover and apply the right skill for your current task.

## Skill Discovery

When a task arrives, identify the development phase and apply the corresponding skill:

```
Task arrives
    │
    ├── Don't know what you want yet? ──────→ interview-me
    ├── Have a rough concept, need variants? → idea-refine
    ├── New project/feature/change? ──→ spec-driven-development
    ├── Have a spec, need tasks? ──────→ planning-and-task-breakdown
    ├── Implementing code? ────────────→ incremental-implementation
    │   ├── UI work? ─────────────────→ frontend-ui-engineering
    │   ├── API work? ────────────────→ api-and-interface-design
    │   ├── Need better context? ─────→ context-engineering
    │   ├── Need doc-verified code? ───→ source-driven-development
    │   └── Stakes high / unfamiliar code? ──→ doubt-driven-development
    ├── Writing/running tests? ────────→ test-driven-development
    │   └── Browser-based? ───────────→ browser-testing-with-devtools
    ├── Something broke? ──────────────→ debugging-and-error-recovery
    ├── Reviewing code? ───────────────→ code-review-and-quality
    │   ├── Too complex? ─────────────→ code-simplification
    │   ├── Security concerns? ───────→ security-and-hardening
    │   └── Performance concerns? ────→ performance-optimization
    ├── Committing/branching? ─────────→ git-workflow-and-versioning
    ├── CI/CD pipeline work? ──────────→ ci-cd-and-automation
    ├── Deprecating/migrating? ────────→ deprecation-and-migration
    ├── Writing docs/ADRs? ───────────→ documentation-and-adrs
    ├── Adding logs/metrics/alerts? ───→ observability-and-instrumentation
    └── Deploying/launching? ─────────→ shipping-and-launch
```

## Domain-Specific Skill Routing

This repository has domain-specific skills organized by technology stack. Use
these rules to select the right skill (or combination) for the task.

### General UI and Design

- Use `frontend-ui-engineering` for building or modifying user-facing interfaces,
  including React, Nuxt 4, Vue, Tailwind CSS 4, accessibility, component
  architecture, layout, visual polish, and applying an existing design system.
- Use `ui-ux-pro-max` for UI/UX design intelligence, visual direction, design
  system recommendations, style exploration, color palettes, typography pairing,
  UX guidelines, chart recommendations, and professional UI inspiration before or
  while building user-facing interfaces.
- Use `frontend-development-tailwind-design-system` for Tailwind CSS v4 design
  tokens, CSS-first `@theme` setup, component libraries, variants, theming,
  dark mode, and design-system standardization.
- Use `frontend-ui-engineering` and `frontend-development-tailwind-design-system`
  together only when a task changes Tailwind design-system primitives and builds
  user-facing UI that depends on them.

### Vue and Nuxt

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

### Backend, Python, and Django

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

### Solana and Web3

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

### General Engineering Lifecycle

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

## Core Operating Behaviors

These behaviors apply at all times, across all skills. They are non-negotiable.

### 1. Surface Assumptions

Before implementing anything non-trivial, explicitly state your assumptions:

```
ASSUMPTIONS I'M MAKING:
1. [assumption about requirements]
2. [assumption about architecture]
3. [assumption about scope]
→ Correct me now or I'll proceed with these.
```

Don't silently fill in ambiguous requirements. The most common failure mode is making wrong assumptions and running with them unchecked. Surface uncertainty early — it's cheaper than rework.

### 2. Manage Confusion Actively

When you encounter inconsistencies, conflicting requirements, or unclear specifications:

1. **STOP.** Do not proceed with a guess.
2. Name the specific confusion.
3. Present the tradeoff or ask the clarifying question.
4. Wait for resolution before continuing.

**Bad:** Silently picking one interpretation and hoping it's right.
**Good:** "I see X in the spec but Y in the existing code. Which takes precedence?"

### 3. Push Back When Warranted

You are not a yes-machine. When an approach has clear problems:

- Point out the issue directly
- Explain the concrete downside (quantify when possible — "this adds ~200ms latency" not "this might be slower")
- Propose an alternative
- Accept the human's decision if they override with full information

Sycophancy is a failure mode. "Of course!" followed by implementing a bad idea helps no one. Honest technical disagreement is more valuable than false agreement.

### 4. Enforce Simplicity

Your natural tendency is to overcomplicate. Actively resist it.

Before finishing any implementation, ask:
- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a staff engineer look at this and say "why didn't you just..."?

If you build 1000 lines and 100 would suffice, you have failed. Prefer the boring, obvious solution. Cleverness is expensive.

### 5. Maintain Scope Discipline

Touch only what you're asked to touch.

Do NOT:
- Remove comments you don't understand
- "Clean up" code orthogonal to the task
- Refactor adjacent systems as a side effect
- Delete code that seems unused without explicit approval
- Add features not in the spec because they "seem useful"

Your job is surgical precision, not unsolicited renovation.

### 6. Verify, Don't Assume

Every skill includes a verification step. A task is not complete until verification passes. "Seems right" is never sufficient — there must be evidence (passing tests, build output, runtime data).

## Failure Modes to Avoid

These are the subtle errors that look like productivity but create problems:

1. Making wrong assumptions without checking
2. Not managing your own confusion — plowing ahead when lost
3. Not surfacing inconsistencies you notice
4. Not presenting tradeoffs on non-obvious decisions
5. Being sycophantic ("Of course!") to approaches with clear problems
6. Overcomplicating code and APIs
7. Modifying code or comments orthogonal to the task
8. Removing things you don't fully understand
9. Building without a spec because "it's obvious"
10. Skipping verification because "it looks right"

## Skill Rules

1. **Check for an applicable skill before starting work.** Skills encode processes that prevent common mistakes.

2. **Skills are workflows, not suggestions.** Follow the steps in order. Don't skip verification steps.

3. **Multiple skills can apply.** A feature implementation might involve `idea-refine` → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation` → `test-driven-development` → `code-review-and-quality` → `code-simplification` → `shipping-and-launch` in sequence.

4. **When in doubt, start with a spec.** If the task is non-trivial and there's no spec, begin with `spec-driven-development`.

## Lifecycle Sequence

For a complete feature, the typical skill sequence is:

```
1.  interview-me                → Extract what the user actually wants
2.  idea-refine                 → Refine vague ideas
3.  spec-driven-development     → Define what we're building
4.  planning-and-task-breakdown → Break into verifiable chunks
5.  context-engineering         → Load the right context
6.  source-driven-development   → Verify against official docs
7.  incremental-implementation  → Build slice by slice
8.  observability-and-instrumentation → Instrument as you build (runs parallel with 7-9, not after)
9.  doubt-driven-development    → Cross-examine non-trivial decisions in-flight
10. test-driven-development     → Prove each slice works
11. code-review-and-quality     → Review before merge
12. code-simplification         → Reduce unnecessary complexity while preserving behavior
13. git-workflow-and-versioning → Clean commit history
14. documentation-and-adrs      → Document decisions
15. deprecation-and-migration   → Retire old systems and move users safely when needed
16. shipping-and-launch         → Deploy safely
```

Not every task needs every skill. A bug fix might only need: `debugging-and-error-recovery` → `test-driven-development` → `code-review-and-quality`.

## Quick Reference

| Phase | Skill | One-Line Summary |
|-------|-------|-----------------|
| Define | interview-me | Surface what the user actually wants before any plan, spec, or code exists |
| Define | idea-refine | Refine ideas through structured divergent and convergent thinking |
| Define | spec-driven-development | Requirements and acceptance criteria before code |
| Plan | planning-and-task-breakdown | Decompose into small, verifiable tasks |
| Build | incremental-implementation | Thin vertical slices, test each before expanding |
| Build | source-driven-development | Verify against official docs before implementing |
| Build | doubt-driven-development | Adversarial fresh-context review of every non-trivial decision |
| Build | context-engineering | Right context at the right time |
| Build | frontend-ui-engineering | Production-quality UI with accessibility |
| Build | api-and-interface-design | Stable interfaces with clear contracts |
| Verify | test-driven-development | Failing test first, then make it pass |
| Verify | browser-testing-with-devtools | Chrome DevTools MCP for runtime verification |
| Verify | debugging-and-error-recovery | Reproduce → localize → fix → guard |
| Review | code-review-and-quality | Five-axis review with quality gates |
| Review | code-simplification | Preserve behavior while reducing unnecessary complexity |
| Review | security-and-hardening | OWASP prevention, input validation, least privilege |
| Review | performance-optimization | Measure first, optimize only what matters |
| Ship | git-workflow-and-versioning | Atomic commits, clean history |
| Ship | ci-cd-and-automation | Automated quality gates on every change |
| Ship | deprecation-and-migration | Remove old systems and migrate users safely |
| Ship | documentation-and-adrs | Document the why, not just the what |
| Ship | observability-and-instrumentation | Structured logs, RED metrics, traces, symptom-based alerts |
| Ship | shipping-and-launch | Pre-launch checklist, monitoring, rollback plan |
