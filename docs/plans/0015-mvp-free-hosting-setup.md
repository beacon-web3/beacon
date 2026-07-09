# MVP Free Hosting Setup

## Status

Draft

## Context

Beacon needs a production-like MVP environment for testing the full Nuxt,
Django, PostgreSQL, and Solana integration path without committing to paid
infrastructure before the product loop is validated.

Relevant specs and docs:

- `docs/architecture/system-design.md`
- `docs/decisions/0010-mvp-free-hosting-stack.md`
- `docs/development/database.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/product/roadmap.md`
- `apps/api/README.md`
- `apps/web/README.md`

## Objective

Create a low-cost production-like deployment path with:

- Nuxt frontend on Vercel free tier.
- Django API on Render free tier.
- PostgreSQL on Aiven free tier.
- Explicit environment configuration for cross-origin session-cookie auth.
- Health checks and smoke-test steps that prove the deployed stack is reachable.
- Manual blockers surfaced before provider accounts, secrets, domains, OAuth, or
  Solana indexing decisions are required.

## Recommended MVP Stack

Use this stack for the first production-like MVP unless a manual blocker changes
the decision:

```text
Frontend: Vercel for Nuxt
Backend API: Render free tier for Django and Django REST Framework
Database: Aiven free-tier managed PostgreSQL
Solana: frontend wallet signing for user-approved transactions, with Django for
app-owned API state and later indexed state
Future worker/indexer: separate process or service, not the sleeping free Render
web service
```

This recommendation optimizes for fast MVP deployment, low DevOps overhead,
standard components, and a clean path to later self-hosting.

## Stack Rationale

### Vercel For Nuxt

Vercel is the preferred frontend host because the MVP should not spend scarce
engineering time on frontend infrastructure. It provides simple Git-based
deployments, automatic HTTPS, preview deployments, and a well-supported path for
Nuxt applications.

The frontend remains portable if Beacon later self-hosts because the app is still
a standard Nuxt application. Avoid making Vercel-specific serverless functions or
edge behavior required for core product logic.

### Render For Django

Render is the recommended first Django host because it is the fastest low-ops way
to put the existing backend online. It supports GitHub-connected deploys,
environment variables, custom domains, HTTPS, and normal long-running web
processes without requiring the team to set up Google Cloud project structure,
container deployment, IAM, or billing workflows up front.

The accepted tradeoff is that Render free services can sleep after inactivity,
causing cold starts. That is acceptable for early MVP testing because speed to
learning matters more than perfect uptime. It is not acceptable for continuous
Solana WebSocket listeners, durable indexing loops, cron-like reconciliation, or
background workers.

Cloud Run remains the stronger alternative if faster scale-to-zero cold starts,
Docker-native deployment, and a more production-shaped cloud path become more
important than setup simplicity.

### Aiven For PostgreSQL

Aiven is the recommended first managed PostgreSQL provider because it behaves
more like a traditional always-on database. That is useful for a Django backend
and safer for a Web3 product that may later add polling, reconciliation,
indexing, or background jobs.

Neon remains a strong alternative when database branching, serverless workflows,
or preview database environments matter more than always-on behavior. If Neon is
chosen later, the implementation should use the provider's pooled connection
string or a conservative Django connection-persistence setting.

Do not use Render free PostgreSQL for durable MVP data because free-tier database
retention and expiration policies can make it unsuitable for signup records,
recommendations, profile data, or indexed chain state that must survive.

### Solana Boundary

For the initial hosted MVP, keep Solana behavior simple:

- Use the frontend wallet flow for user-approved signing.
- Use direct client RPC reads only for simple non-authoritative display needs
  where appropriate.
- Use Django for Beacon-owned API state and eventually indexed chain state.
- Add a separate worker/indexer only when persistent event monitoring is actually
  required.

Do not put always-on Solana event monitoring inside a sleeping free Render web
service.

## Self-Hosting Portability

The recommended stack is intentionally portable because it uses standard
components rather than a backend-as-a-service architecture:

- Nuxt can move from Vercel to a VPS, Docker Compose, Coolify, Dokploy, CapRover,
  Fly.io, Kubernetes, or static/Node hosting.
- Django can move from Render to Docker on a VPS, Cloud Run, Fly.io, Hetzner,
  DigitalOcean, AWS, GCP, or Kubernetes.
- Aiven PostgreSQL can migrate to self-hosted PostgreSQL with `pg_dump` and
  `pg_restore`.
- Django already uses `DATABASE_URL`, so database migration should mostly be an
  environment-variable and data-restore change.
- Auth and business logic remain owned by Django, avoiding Supabase/Firebase/Auth0
  lock-in for core account and product behavior.

Recommended later self-hosted shape:

```text
Reverse proxy: Caddy or Traefik
Frontend: Nuxt container or generated static assets
Backend: Django container with Gunicorn or Uvicorn
Database: PostgreSQL, either self-hosted or separately managed
Worker/indexer: separate Django/Celery/RQ or custom Solana indexer process
Scheduler: cron, Celery beat, or provider-native scheduler
TLS: Caddy automatic HTTPS or equivalent
Deployment: Docker Compose first; Kubernetes only when scale justifies it
```

To preserve this path, avoid depending on provider-specific features for core app
behavior, including Vercel-only backend functions, Render-only cron jobs as the
only indexing mechanism, Aiven-specific PostgreSQL extensions that cannot be
self-hosted, or provider-managed auth as the source of truth.

## Architecture Decisions

- Keep the MVP deployment as a modular monolith: one Nuxt app, one Django API,
  one managed PostgreSQL database, and Solana programs/RPC outside the web host.
- Prefer Render for the first Django host because fastest setup and low DevOps
  burden matter most at MVP stage.
- Prefer Cloud Run if the team accepts more setup in exchange for Docker-native
  deployment and faster scale-to-zero cold starts.
- Prefer Aiven for the first managed PostgreSQL database because always-on
  behavior is simpler for Django and future Web3 reconciliation work.
- Prefer Neon instead if database branching and serverless preview workflows
  become more important than always-on behavior.
- Do not use Render free PostgreSQL for durable MVP data.
- Do not place continuous Solana RPC WebSocket listeners or durable event
  indexing inside a sleeping free web service until the indexing boundary is
  resolved.

## Manual Blockers

- [ ] Provider account access: developer must confirm access to Vercel and either
  Render or Google Cloud.
- [ ] Backend host confirmation: developer must confirm Render free tier or
  intentionally override to Cloud Run before backend deployment files are
  finalized.
- [ ] Database provider confirmation: developer must confirm Aiven or
  intentionally override to Neon before production `DATABASE_URL` is configured.
- [ ] Billing or credit-card requirement: developer must complete any provider
  sign-up requirement, especially if Cloud Run is selected.
- [ ] Region selection: developer must choose frontend, backend, and database
  regions close enough to reduce latency for the intended MVP testers.
- [ ] Secrets: developer must create or provide production values through provider
  secret managers, never in repository files.
- [ ] Domain decision: developer must decide whether to use provider preview
  domains first or configure custom domains.
- [ ] Google OAuth redirect URIs: developer must add production callback URLs in
  the Google Cloud Console before social auth can work in production.
- [ ] Email provider: developer must choose and configure production email
  delivery before relying on email verification or password reset in production.
- [ ] reCAPTCHA keys: developer must create production site and secret keys if
  `RECAPTCHA_ENABLED=true` in production.
- [ ] Solana event monitoring boundary: developer must decide whether MVP event
  reads are handled by Django, a separate worker/indexer, scheduled jobs, or
  direct Nuxt client RPC reads.

## Phase 1: Provider Decisions And Environment Inventory

### Task 1: Confirm Hosting Providers

Description: Choose the concrete free-tier providers for frontend, backend, and
database before writing provider-specific deployment configuration.

Acceptance criteria:

- [ ] Frontend provider is confirmed as Vercel.
- [ ] Backend provider is confirmed as Render, or the plan records an explicit
  override to Cloud Run.
- [ ] Database provider is confirmed as Aiven, or the plan records an explicit
  override to Neon.
- [ ] Any credit-card or billing sign-up requirement is documented as completed
  or blocking.

Verification:

- [ ] Manual check: developer confirms provider choices and account access in the
  implementation session before proceeding.

Dependencies: None.

Files likely touched:

- `docs/plans/0015-mvp-free-hosting-setup.md`
- Optional provider-specific deployment docs.

Estimated scope: Small.

Manual blocker: Provider account access and provider selection.

### Task 2: Build Production Environment Variable Checklist

Description: Create a deployment checklist for all environment variables needed
by Vercel, the backend host, and the managed PostgreSQL provider.

Acceptance criteria:

- [ ] Backend checklist covers `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`,
  `ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`,
  `CSRF_TRUSTED_ORIGINS`, `FRONTEND_BASE_URL`, secure cookie settings, HSTS
  settings, email settings, reCAPTCHA settings, and Google OAuth settings.
- [ ] Frontend checklist covers `NUXT_PUBLIC_API_BASE_URL` and
  `NUXT_PUBLIC_RECAPTCHA_SITE_KEY`.
- [ ] Checklist explicitly says secrets must be set in provider dashboards or
  secret managers, not committed.

Verification:

- [ ] Documentation review confirms every currently supported variable in
  `apps/api/.env.example` and `apps/web/README.md` is addressed.

Dependencies: Task 1.

Files likely touched:

- `apps/api/README.md`
- `apps/web/README.md`
- Optional `docs/development/deployment.md` if created.

Estimated scope: Medium.

Manual blocker: Production secret values and domains are not available to agents
unless the developer enters them in provider dashboards.

## Phase 2: Database Setup

### Task 3: Configure Managed PostgreSQL

Description: Create the managed PostgreSQL project and prepare Django to connect
to it using `DATABASE_URL`.

Acceptance criteria:

- [ ] Neon or Aiven database exists in the selected region.
- [ ] `DATABASE_URL` is configured only in the backend host's environment.
- [ ] If Neon is selected, the provider-recommended pooled connection string or a
  conservative Django connection persistence setting is used.
- [ ] Local development continues to use Docker Compose PostgreSQL by default.

Verification:

- [ ] Manual check: developer confirms provider database is created and
  connection string is stored in the backend host.
- [ ] Backend check after deployment: `python manage.py migrate` succeeds on the
  production-like database.

Dependencies: Task 1.

Files likely touched:

- `apps/api/beacon_api/settings.py` if a connection-persistence env setting is
  needed.
- `apps/api/.env.example` if a non-secret optional setting is added.
- `docs/development/database.md`.

Estimated scope: Medium.

Manual blocker: Database provider account, region, and secret connection string.

## Phase 3: Backend Deployment

### Task 4: Add Backend Health Check

Description: Add a minimal public health endpoint suitable for provider health
checks and smoke tests.

Acceptance criteria:

- [ ] Public endpoint returns `200 OK` without authentication.
- [ ] Endpoint does not expose secrets, database credentials, stack traces, or
  private operational details.
- [ ] Endpoint is documented for deployment verification.

Verification:

- [ ] Backend tests cover the health endpoint.
- [ ] Local command passes: `cd apps/api && .venv/bin/pytest` or focused health
  endpoint tests.

Dependencies: Task 2.

Files likely touched:

- `apps/api/beacon_api/urls.py`
- Backend tests.
- `apps/api/README.md`.

Estimated scope: Small.

### Task 5: Add Backend Provider Configuration

Description: Add the minimal deployment configuration for the selected Django
host.

Acceptance criteria:

- [ ] Render path includes the required build/start commands and health check
  path, or Cloud Run path includes Docker build/deploy instructions.
- [ ] Static files, migrations, runtime command, and Python version expectations
  are documented.
- [ ] Configuration avoids committed secrets.
- [ ] Cold-start behavior is documented as expected free-tier behavior.

Verification:

- [ ] Backend build/check command passes locally before provider deployment.
- [ ] Provider deployment completes and health endpoint returns `200 OK`.

Dependencies: Tasks 2, 3, and 4.

Files likely touched:

- Provider-specific config file if needed.
- `apps/api/README.md`.
- Optional deployment documentation.

Estimated scope: Medium.

Manual blocker: Backend provider choice and dashboard access.

## Phase 4: Frontend Deployment

### Task 6: Configure Vercel Nuxt Deployment

Description: Deploy the Nuxt app from `apps/web` to Vercel and point it at the
production-like Django API.

Acceptance criteria:

- [ ] Vercel project root/build settings target `apps/web`.
- [ ] `NUXT_PUBLIC_API_BASE_URL` points to the deployed Django API.
- [ ] `NUXT_PUBLIC_RECAPTCHA_SITE_KEY` is set when production reCAPTCHA is
  enabled.
- [ ] Vercel preview or production URL is added to Django `ALLOWED_HOSTS` where
  needed, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`.

Verification:

- [ ] Vercel deployment succeeds.
- [ ] Manual smoke test reaches the frontend and performs a safe backend request.
- [ ] Browser devtools show no unexpected CORS or CSRF failures for safe reads.

Dependencies: Tasks 2 and 5.

Files likely touched:

- `apps/web/README.md`.
- Optional Vercel deployment docs.

Estimated scope: Medium.

Manual blocker: Vercel account/project access and final frontend URL.

## Phase 5: Auth, Email, And OAuth Production Readiness

### Task 7: Configure Production Auth Dependencies

Description: Make email verification, password reset, Google social auth, and
reCAPTCHA work against production-like URLs.

Acceptance criteria:

- [ ] Production email provider is configured through backend environment
  variables.
- [ ] Google OAuth production redirect URI matches the deployed backend callback
  URL.
- [ ] `FRONTEND_BASE_URL` points to the deployed frontend URL.
- [ ] Secure cookie and HTTPS settings are enabled for production.
- [ ] reCAPTCHA is either explicitly enabled with production keys or intentionally
  disabled for limited internal testing.

Verification:

- [ ] Manual smoke test covers signup, email verification delivery, login,
  logout, password reset request, and Google auth start/callback behavior.

Dependencies: Tasks 5 and 6.

Files likely touched:

- Documentation only unless new settings are needed.

Estimated scope: Medium.

Manual blocker: Email provider credentials, Google OAuth console access, and
reCAPTCHA production keys.

## Phase 6: Solana Integration Boundary

### Task 8: Resolve Solana Event Monitoring Architecture

Description: Decide how the production-like MVP reads and reconciles Solana state
before implementing any persistent event monitoring.

Acceptance criteria:

- [ ] Decision identifies whether MVP chain reads are direct frontend RPC reads,
  Django API reads, scheduled reconciliation, or a separate worker/indexer.
- [ ] Decision documents why the selected approach fits free-tier hosting limits.
- [ ] Any background worker, cron, queue, or WebSocket service requirement is
  added to a follow-up plan before implementation.

Verification:

- [ ] Decision record or architecture doc is updated and linked from this plan.

Dependencies: Tasks 1-7 can proceed without this only for non-chain auth/API
smoke tests. Any chain indexing implementation depends on this task.

Files likely touched:

- `docs/architecture/system-design.md`
- `docs/decisions/`
- Optional follow-up plan under `docs/plans/`.

Estimated scope: Small for decision, larger for implementation follow-up.

Manual blocker: Developer/product decision on Solana monitoring boundary.

## Checkpoint: Production-Like Smoke Test

Run this after Tasks 1-7 and before any public beta traffic.

- [ ] Frontend URL loads over HTTPS.
- [ ] Backend health endpoint returns `200 OK` over HTTPS.
- [ ] Backend OpenAPI docs load over HTTPS.
- [ ] Django migrations have run against the managed database.
- [ ] Signup and login work from the deployed frontend.
- [ ] CSRF-protected unsafe requests work from the deployed frontend.
- [ ] Password reset and email verification deliver email through the production
  email provider.
- [ ] Google social auth redirects to and from the deployed backend.
- [ ] Backend logs are accessible in the selected host.
- [ ] Cold-start behavior is tested and documented.
- [ ] Rollback path is documented for frontend and backend deployments.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Free backend cold starts delay first requests | Medium | Document expected behavior, add health endpoint, consider Cloud Run or paid always-on hosting if unacceptable. |
| Database free-tier limits change | Medium | Record provider and plan details during setup; avoid using expiring free databases for durable MVP data. |
| Cross-origin session auth misconfiguration | High | Explicitly configure `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, secure cookies, and HTTPS settings. |
| Secrets leak into repository docs or config | High | Store secrets only in provider dashboards or secret managers; docs list variable names only. |
| Solana indexing needs always-on compute | High | Block indexing implementation until the worker/indexer architecture is decided. |
| OAuth callback mismatch | Medium | Add deployed callback URLs in Google Console before testing Google social auth. |

## Open Questions

- Should the backend host be Render or Cloud Run for the first production-like
  MVP deployment?
- Should the managed PostgreSQL provider be Neon or Aiven?
- What cold-start delay is acceptable for MVP testers?
- Which provider should handle production email delivery?
- Should production-like MVP testing use provider preview domains or custom
  domains?
- Where should Solana event monitoring and reconciliation run?

## Approval Gate

This plan should remain `Draft` until the manual blockers in Phase 1 are
resolved. Move to `Approved` only after the developer confirms provider choices,
account access, and the intended non-chain deployment scope.
