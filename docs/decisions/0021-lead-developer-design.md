# 0021 — Lead Developer Agent Design

Status: Accepted
Date: 2026-07-15

## Context

The project needed an automated implementation agent that can build features
across Beacon's domains (frontend, backend, web3, shared, documentation) with
proper validation gates. The existing review-agent handles read-only code review,
but there was no agent to drive the build side — reading plans, implementing
tasks, running checks, and coordinating parallel work across domains. The agent
must work within OpenCode's agent framework and avoid name collision with the
default build agent.

## Decision

Add a plan-driven Lead Developer Agent with the following design:

- **Named `lead-developer`** to distinguish from OpenCode's default build agent
  and to convey the orchestration role.
- **Two-mode architecture**: Auto mode routes between direct implementation
  (inline, for small single-domain tasks) and orchestrate mode (specialist
  sub-agents, for multi-domain features) based on task count and domain spread.
- **Plan-driven input**: Reads tasks from `docs/plans/` plan files or from
  standalone task descriptions. Updates plan task statuses as work progresses.
- **Domain-based routing**: Tasks are classified by path prefix into Frontend,
  Backend, Web3, Shared, Documentation, and Config domains.
- **Five specialist sub-agent types**: Frontend, Backend, Web3, Shared, and
  Documentation — each with minimal core skills and dynamic skill loading based
  on task signals.
- **Two-tier skill loading**: Core skills always loaded (3 skills for
  lead-developer, 1-2 per specialist domain). Additional skills loaded
  dynamically when a task clearly signals the need (e.g., Pinia store →
  vue-pinia-best-practices). Skills are not loaded speculatively.
- **Pre-flight and post-flight validation gates**: Domain-specific checks run
  before and after each task. Post-flight failures block subsequent tasks.
- **File ownership boundaries**: In orchestrate mode, each specialist owns its
  domain path and may not write outside it. Cross-domain integration is handled
  by the orchestrator.
- **Error recovery**: Failed tasks are rolled back (`git checkout`), reported,
  and do not block isolated subsequent tasks.
- **Three core skills**: incremental-implementation, test-driven-development,
  security-and-hardening.
- **Dual documentation**: Agent instructions
  (`.opencode/agents/lead-developer.md`) are the source of truth for agent
  behavior. Human docs (`docs/development/lead-developer.md`) cover usage, CLI
  examples, and configuration reference.

## Alternatives Considered

- **Single-mode build agent** (direct only): Rejected because multi-domain
  features need parallel specialists with domain expertise; a single agent
  accumulates too much context for cross-domain work.
- **Build-agent that always commits**: Rejected because commits should be
  explicit user actions; the agent should implement and validate, not decide
  when to commit.
- **Separate agents per domain**: Rejected because it fragments invocation and
  makes auto-routing impossible; a single agent with specialist delegation is
  simpler to invoke and maintain.
- **Build-agent without validation gates**: Rejected because unvalidated changes
  accumulate technical debt; pre/post-flight checks catch issues early.
- **Always loading all domain skills**: Rejected because it wastes context
  tokens; a two-tier approach loads skills dynamically based on actual task
  needs.
- **Pre-registered specialist agent types**: Rejected because it multiplies
  agent configs; dynamic prompt construction with the `task` tool keeps the
  agent count at two (review-agent + lead-developer).

## Consequences

- Implementation quality scales with the skill library; new domain skills
  automatically improve specialist capability.
- Orchestrate mode introduces latency from parallel sub-agent spawning, but
  this is acceptable for multi-domain features where domain expertise matters.
- Two-tier skill loading keeps specialist context lean (~8K tokens base) while
  still getting deep expertise when needed.
- File ownership boundaries prevent merge conflicts but require cross-domain
  integration to be serialized through the orchestrator.
- Pre/post-flight checks add rigor but may need updating as the project's tool
  chain evolves.
- Dual documentation requires keeping two files in sync; cross-references and
  clear ownership mitigate drift.

## Links

- Agent config: `.opencode/agents/lead-developer.json`
- Agent instructions: `.opencode/agents/lead-developer.md`
- Human docs: `docs/development/lead-developer.md`
- Review agent (parallel design): `docs/decisions/0020-review-agent-design.md`
- AGENTS.md: Custom Agents section
