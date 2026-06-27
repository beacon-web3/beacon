# 0010: MVP Free Hosting Stack

## Status

Proposed

## Date

2026-06-27

## Context

Beacon needs a low-cost production-like MVP environment for testing the Nuxt,
Django, PostgreSQL, and Solana integration path before paid infrastructure is
justified.

The frontend can use Vercel's free tier for early production testing. The
backend and database need matching free or near-free services that keep the MVP
simple, avoid premature infrastructure complexity, and make operational limits
visible to developers.

Key constraints:

- The MVP should keep Django as a modular monolith rather than introducing
  microservices.
- PostgreSQL should remain the primary relational database.
- Free application hosting commonly has cold starts or scale-to-zero behavior.
- Render free web services may spin down after inactivity, causing delayed first
  requests.
- Render free PostgreSQL is unsuitable for durable MVP data because free
  databases can expire or be deleted after a provider-defined trial window.
- Serverless PostgreSQL providers may pause compute or prefer connection pooling.
- Web3 event indexing or continuous Solana RPC WebSocket listeners may not fit a
  sleeping web service.

## Decision

Use the following proposed hosting shape for the initial production-like MVP
environment:

- Frontend: Vercel free tier for `apps/web`.
- Backend API: Render free web service for `apps/api` as the first low-ops Django
  host, unless Cloud Run is chosen during implementation because Docker-based
  deployment and faster scale-to-zero cold starts are preferred.
- Database: Neon free tier or Aiven free tier for managed PostgreSQL, selected
  before deployment based on account availability, region, free-tier durability,
  and whether always-on compute is required.

Render-hosted Django should connect to the external managed PostgreSQL database,
not to Render free PostgreSQL, for any MVP data that must survive beyond short
experiments.

If Neon is selected, Django should use the provider's recommended pooled
connection string or conservative persistent connection settings. If Aiven is
selected, Django can use the managed instance connection string with normal
Django PostgreSQL settings, subject to the provider's current connection and
resource limits.

This decision does not decide where Solana event monitoring lives. Continuous
indexing, long-running jobs, or RPC WebSocket listeners remain a manual blocker
until the architecture decision is made.

## Alternatives Considered

### Render backend with Render free PostgreSQL

- Pros: Simple single-provider setup and good developer experience.
- Cons: Free database durability limits make it risky for any MVP data that must
  persist.
- Rejected for durable MVP data; acceptable only for disposable experiments.

### Google Cloud Run backend with Neon or Aiven PostgreSQL

- Pros: Generous free tier, fast scale-to-zero cold starts, Docker-native,
  production-shaped deployment.
- Cons: Requires billing account or credit card and more initial DevOps setup
  than Render.
- Kept as an implementation option if the team prefers Docker deployment or lower
  cold-start latency.

### Paid infrastructure from the start

- Pros: Fewer free-tier limits and more predictable always-on behavior.
- Cons: Adds cost before Beacon validates the MVP loop.
- Deferred until MVP traffic, uptime, background worker, or database needs exceed
  free-tier constraints.

## Consequences

- Cold starts must be documented as expected behavior for free backend hosting.
- Production environment variables must explicitly configure `ALLOWED_HOSTS`,
  CORS origins, CSRF trusted origins, secure cookies, frontend base URL, database
  URL, email settings, reCAPTCHA settings, and Google OAuth redirect settings.
- Backend health checks and smoke tests should be added before relying on the
  free production-like environment.
- Any task requiring persistent Solana indexing, background workers, cron jobs,
  or WebSocket listeners must stop at a manual blocker until a worker/indexer
  hosting decision is made.
- Free tiers are suitable for MVP validation, not a promise of production
  reliability.

## Related Specs

- `docs/architecture/system-design.md`
- `docs/development/database.md`
- `docs/product/open-questions.md`
- `docs/product/assumptions.md`
- `docs/plans/0015-mvp-free-hosting-setup.md`
