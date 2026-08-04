# 0023: MVP Solana Event Monitoring Boundary

## Status

Accepted

## Date

2026-08-04

## Context

Beacon's production-like MVP runs Nuxt + Django on Vercel Hobby (Vercel
Services, one domain) with Neon free-tier PostgreSQL. Free-tier web hosting is
ephemeral: serverless functions cannot hold long-lived connections, and a
sleeping web service cannot run continuous Solana RPC WebSocket listeners or
durable background jobs (see `docs/decisions/0010-mvp-free-hosting-stack.md`
and `docs/architecture/system-design.md`).

No Solana program is implemented yet (`apps/contracts/` is an empty workspace),
so this boundary is decided before contract work starts rather than invented
during deployment.

The MVP on-chain actions are wallet connection, `0.01 SOL` support
contributions, and `0.2 SOL` curator stake locks. The backend must learn that
these happened and serve recorded state, but it must never be the source of
truth for economic balances.

## Decision

Use hybrid pull for MVP Solana event monitoring:

- The frontend reads wallet, account, and balance state directly from an RPC
  node for display.
- Django verifies support and stake transactions on demand via RPC (transaction
  signature lookup) at the point of recording, then serves recorded state from
  PostgreSQL.
- No persistent WebSocket listener, no always-on indexer, and no scheduled cron
  in the MVP hosting shape.

The chain remains the source of truth for balances; Django is a cache of
verified state, never the custody authority.

When history and aggregation become required (reward milestones, badge minting,
full treasury dashboards), a separate worker/indexer is added through a follow-up
plan before implementation.

## Alternatives Considered

### Dedicated worker/indexer (always-on WebSocket listener)

- Pros: Real-time event ingestion and rich history.
- Cons: Requires its own always-on host, contradicting the free-tier MVP stack;
  no MVP feature needs real-time aggregation.
- Rejected for MVP; planned as a follow-up when history becomes required.

### Scheduled reconciliation (cron)

- Pros: Periodic refresh without a dedicated process.
- Cons: Adds a last-processed cursor and backfill subsystem for no MVP need;
  Vercel cron limits on Hobby.
- Rejected for MVP.

### Django-only reads (no direct frontend RPC)

- Pros: One read path.
- Cons: Wallet display requires direct chain state; routing all reads through
  Django adds latency and RPC cost for no benefit.
- Rejected.

### Frontend-only reads (no Django verification)

- Pros: Simplest.
- Cons: The backend must verify support and stake events before recording app
  state; unverified DB records would break trust in recorded state.
- Rejected.

## Consequences

- Django needs an RPC client configuration (provider endpoint) when contract
  integration begins; that is a follow-up task, not part of this plan.
- Displayed balances come from the wallet/RPC; recorded history comes from
  PostgreSQL. Numbers may briefly differ until a verification is recorded.
- No background worker, cron, queue, or WebSocket service is part of the MVP
  hosting shape, and none may be added without a follow-up plan.
- Revisit this boundary if MVP learning shows a feature needs instant
  chain-event reaction.

## Related Specs

- `docs/architecture/system-design.md`
- `docs/decisions/0010-mvp-free-hosting-stack.md`
- `docs/plans/0015-mvp-free-hosting-setup.md`
- `docs/product/mvp.md`
- `docs/product/open-questions.md`
- `docs/product/assumptions.md`
