# 0020 — Review Agent Design

Status: Accepted
Date: 2026-07-15

## Context

The project needed an automated code review gate that catches security,
performance, architecture, and testing issues before they reach production.
The review agent must work within OpenCode's agent framework, support both
small focused changes and wide multi-domain diffs, and produce actionable
findings without modifying code.

## Decision

Add a read-only Review Agent with the following design:

- **Two-mode architecture**: Auto mode routes between direct review (inline,
  for small diffs) and orchestrate mode (specialist sub-agents, for wide or
  multi-domain diffs) based on file count and diff size thresholds.
- **Domain-based routing**: Files are classified by path prefix into Frontend,
  Backend, Web3, Shared, Documentation, and Config domains. Each domain has
  dedicated specialist skills.
- **Four core skills always loaded**: code-review-and-quality,
  security-and-hardening, performance-optimization, code-simplification.
- **Findings-only output**: No code changes, no commits. The report includes
  severity, location (file:line), description, evidence, and suggested skills
  for fixing.
- **Dual documentation**: Agent instructions (`.opencode/agents/review-agent.md`)
  are the source of truth for agent behavior. Human docs
  (`docs/development/review-agent.md`) cover usage, CLI examples, and
  configuration reference.

## Alternatives Considered

- **Single-mode review agent** (direct only): Rejected because large cross-domain
  diffs would produce overwhelming, unfocused reports without domain
  specialization.
- **Separate agents per domain**: Rejected because it fragments invocation and
  makes auto-routing impossible; a single agent with specialist delegation is
  simpler to invoke and maintain.
- **Modifying agent that applies fixes**: Rejected because review and fix should
  be separate concerns; the reviewer should not have write access.

## Consequences

- Review quality scales with the skill library; new domains or skills
  automatically improve coverage.
- Orchestrate mode introduces latency from parallel sub-agent spawning, but
  this is acceptable for wide diffs where thoroughness matters.
- Dual documentation requires keeping two files in sync; cross-references and
  clear ownership (agent instructions = behavior, human docs = usage) mitigate
  drift.

## Links

- Agent config: `.opencode/agents/review-agent.json`
- Agent instructions: `.opencode/agents/review-agent.md`
- Human docs: `docs/development/review-agent.md`
- AGENTS.md: Custom Agents section
