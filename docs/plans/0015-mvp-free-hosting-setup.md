# MVP Free Hosting Setup

## Status

Approved (2026-08-03): Phase 1 blockers resolved and the non-chain deployment is
confirmed live — `GET /api/health/` returns `{"status": "ok"}` over HTTPS on
beacon-web3.vercel.app. Email provider resolved (2026-08-04): Google SMTP with a
Gmail app password. CAPTCHA resolved (2026-08-04): Cap proof-of-work captcha
(`capjs-core`) is implemented end to end. Task 8 remains blocked on its own
manual blocker; Task 7 is partially complete (email configured, CAPTCHA
implemented, Google OAuth redirect URIs still pending).

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

- Nuxt frontend on Vercel Hobby.
- Django API on Vercel Hobby through Vercel Services.
- PostgreSQL on Neon free tier.
- Explicit environment configuration for cross-origin session-cookie auth.
- Health checks and smoke-test steps that prove the deployed stack is reachable.
- Manual blockers surfaced before provider accounts, secrets, domains, OAuth, or
  Solana indexing decisions are required.

## Recommended MVP Stack

Use this stack for the first production-like MVP unless a manual blocker changes
the decision:

```text
Frontend: Vercel Hobby for Nuxt
Backend API: Vercel Hobby for Django and Django REST Framework (Vercel Services,
same project and domain as the frontend)
Database: Neon free-tier managed PostgreSQL
Solana: frontend wallet signing for user-approved transactions, with Django for
app-owned API state and later indexed state
Future worker/indexer: separate process or service, not a Vercel Function
```

This recommendation optimizes for fast MVP deployment, low DevOps overhead,
standard components, and a clean path to later self-hosting.

## Stack Rationale

Decision update (2026-08-03): Task 1 selected Vercel Hobby for both Nuxt and
Django (Vercel Services, one domain) and Neon free tier for PostgreSQL. The
sections below retain the original analysis that led there; Render and Aiven
remain fallbacks, not the chosen stack.

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
- Prefer Vercel for the first Django host because it shares the frontend project
  and domain through Vercel Services, removing separate cross-origin auth
  configuration.
- Prefer Cloud Run if the team accepts more setup in exchange for Docker-native
  deployment and faster scale-to-zero cold starts.
- Prefer Neon for the first managed PostgreSQL database because the free tier
  requires no credit card and includes connection pooling.
- Prefer Aiven instead if always-on behavior without scale-to-zero outweighs the
  sign-up requirement.
- Do not use Render free PostgreSQL for durable MVP data.
- Do not place continuous Solana RPC WebSocket listeners or durable event
  indexing inside a sleeping free web service until the indexing boundary is
  resolved.

## Manual Blockers

- [x] Provider account access: confirmed for Vercel and Neon.
- [x] Backend host confirmation: Vercel Hobby for Django (Vercel Services).
- [x] Database provider confirmation: Neon free tier.
- [x] Account sign-up: no credit card required; accounts created and access
  confirmed.
- [x] Region selection: Neon database in us-east-2.
- [x] Secrets: boot-set secrets (`DJANGO_SECRET_KEY`, `DATABASE_URL`) stored in
  the Vercel dashboard, never in repository files.
- [x] Domain decision: provider preview domain `beacon-web3.vercel.app`.
- [ ] Google OAuth redirect URIs: pending (Task 7).
- [x] Email provider: Google SMTP (`smtp.gmail.com:587`, TLS, Gmail app
  password) configured through backend environment variables (resolved
  2026-08-04).
- [x] CAPTCHA: Cap proof-of-work captcha (`capjs-core`) implemented end to end
  — Nuxt Nitro routes `apps/web/server/api/cap/challenge.post.ts` and
  `redeem.post.ts` issue/redeem challenges signed with `NUXT_CAPTCHA_SECRET`,
  backend `accounts/captcha.py` verifies the HS256 JWT when
  `CAPTCHA_ENABLED=true` (resolved 2026-08-04). Sharing `CAPTCHA_SECRET` /
  `NUXT_CAPTCHA_SECRET` between the API and frontend enables it.
- [ ] Solana event monitoring boundary: pending (Task 8).

## Phase 1: Provider Decisions And Environment Inventory

### Task 1: Confirm Hosting Providers

Description: Choose the concrete free-tier providers for frontend, backend, and
database before writing provider-specific deployment configuration.

Acceptance criteria:

- [x] Frontend provider is confirmed as Vercel (Hobby).
- [x] Backend provider is confirmed as Vercel Hobby for Django through Vercel
  Services, sharing the frontend project and domain.
- [x] Database provider is confirmed as Neon free tier.
- [x] No credit card is required on Vercel Hobby or Neon free; account sign-up
  and access remain blocking until the developer completes them.

Verification:

- [x] Manual check: developer confirms provider choices and account access in the
  implementation session before proceeding.

Dependencies: None.

Files likely touched:

- `docs/plans/0015-mvp-free-hosting-setup.md`
- Optional provider-specific deployment docs.

Estimated scope: Small.

Manual blocker: Provider account access and provider selection (resolved
2026-08-03).

Status note (2026-08-03): The chosen stack is Vercel Hobby for both Nuxt and
Django (one project, one domain, `/api/*` rewrites to the Django service) plus
Neon free-tier PostgreSQL. No credit card is required on Vercel Hobby or Neon
free. Provider choices and account access are confirmed; the production-like
stack is deployed and `GET /api/health/` returns `{"status": "ok"}` over HTTPS.
Task complete.

### Task 2: Build Production Environment Variable Checklist

Description: Create a deployment checklist for all environment variables needed
by Vercel, the backend host, and the managed PostgreSQL provider.

Acceptance criteria:

- [x] Backend checklist covers `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`,
  `ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`,
  `CSRF_TRUSTED_ORIGINS`, `FRONTEND_BASE_URL`, secure cookie settings, HSTS
  settings, email settings, CAPTCHA settings, and Google OAuth settings.
- [x] Frontend checklist covers `NUXT_PUBLIC_API_BASE_URL` and the shared
  `CAPTCHA_SECRET`.
- [x] Checklist explicitly says secrets must be set in provider dashboards or
  secret managers, not committed.

Verification:

- [x] Documentation review confirms every currently supported variable in
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

- [x] Neon or Aiven database exists in the selected region (Neon,
  ep-billowing-mode-aym1cst4, us-east-2).
- [x] `DATABASE_URL` is configured only in the backend host's environment.
- [x] If Neon is selected, the provider-recommended pooled connection string or a
  conservative Django connection persistence setting is used (pooled string).
- [x] Local development continues to use Docker Compose PostgreSQL by default.

Verification:

- [x] Manual check: developer confirms provider database is created and
  connection string is stored in the backend host.
- [x] Backend check after deployment: `python manage.py migrate` succeeds on the
  production-like database (29 migrations applied 2026-08-03).

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

- [x] Public endpoint returns `200 OK` without authentication.
- [x] Endpoint does not expose secrets, database credentials, stack traces, or
  private operational details.
- [x] Endpoint is documented for deployment verification.

Verification:

- [x] Backend tests cover the health endpoint.
- [x] Local command passes: `cd apps/api && .venv/bin/pytest` or focused health
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

- [x] Vercel Services path includes the required build/start commands and health
  check path (or the Cloud Run path is documented if overridden).
- [x] Static files, migrations, runtime command, and Python version expectations
  are documented.
- [x] Configuration avoids committed secrets.
- [x] Cold-start behavior is documented as expected free-tier behavior.

Verification:

- [x] Backend build/check command passes locally before provider deployment.
- [x] Provider deployment completes and health endpoint returns `200 OK`.

Dependencies: Tasks 2, 3, and 4.

Files likely touched:

- Provider-specific config file if needed.
- `apps/api/README.md`.
- Optional deployment documentation.

Estimated scope: Medium.

Manual blocker: Backend provider choice and dashboard access (resolved
2026-08-03).

## Phase 4: Frontend Deployment

### Task 6: Configure Vercel Nuxt Deployment

Description: Deploy the Nuxt app from `apps/web` to Vercel and point it at the
production-like Django API.

Acceptance criteria:

- [x] Vercel project root/build settings target `apps/web` (via vercel.json
  service root).
- [x] `NUXT_PUBLIC_API_BASE_URL` points to the deployed Django API
  (`https://beacon-web3.vercel.app`).
- [x] `CAPTCHA_SECRET` is set when production CAPTCHA is enabled (not set:
  CAPTCHA intentionally disabled for MVP).
- [x] Vercel preview or production URL is added to Django `ALLOWED_HOSTS` where
  needed, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`.

Verification:

- [x] Vercel deployment succeeds.
- [x] Manual smoke test reaches the frontend and performs a safe backend request
  (2026-08-03: GET /, /fr, /api/health/ → {"status":"ok"}, /api/docs/swagger/ all
  reachable over HTTPS on beacon-web3.vercel.app).
- [x] Browser devtools show no unexpected CORS or CSRF failures for safe reads
  (structurally verified: frontend and API share one domain, so all requests are
  same-site; no cross-origin CORS or CSRF path exists).

Dependencies: Tasks 2 and 5.

Files likely touched:

- `apps/web/README.md`.
- Optional Vercel deployment docs.

Estimated scope: Medium.

Manual blocker: Vercel account/project access and final frontend URL (resolved
2026-08-03). Deployment succeeds, the backend health endpoint is confirmed, and
the frontend page smoke test passed (2026-08-03).

## Phase 5: Auth, Email, And OAuth Production Readiness

### Task 7: Configure Production Auth Dependencies

Description: Make email verification, password reset, Google social auth, and
CAPTCHA work against production-like URLs.

Acceptance criteria:

- [x] Production email provider is configured through backend environment
  variables (Google SMTP: `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`,
  `EMAIL_HOST=smtp.gmail.com`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=true`,
  `EMAIL_USE_SSL=false`, `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` = Gmail address
  and 16-char app password, `DEFAULT_FROM_EMAIL`; resolved 2026-08-04).
- [ ] Google OAuth production redirect URI matches the deployed backend callback
  URL.
- [ ] `FRONTEND_BASE_URL` points to the deployed frontend URL.
- [ ] Secure cookie and HTTPS settings are enabled for production.
- [x] CAPTCHA is either explicitly enabled with a shared `CAPTCHA_SECRET` or
  intentionally disabled for limited internal testing (Cap proof-of-work
  captcha implemented and covered by tests, resolved 2026-08-04).

Verification:

- [ ] Manual smoke test covers signup, email verification delivery, login,
  logout, password reset request, and Google auth start/callback behavior.

Dependencies: Tasks 5 and 6.

Files likely touched:

- Documentation only unless new settings are needed.

Estimated scope: Medium.

Manual blocker: Google OAuth console access (email provider credentials
resolved 2026-08-04 via Google SMTP app password; CAPTCHA implemented
2026-08-04 via Cap proof-of-work).

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

- [x] Frontend URL loads over HTTPS (2026-08-03: / and /fr render on
  beacon-web3.vercel.app).
- [x] Backend health endpoint returns `200 OK` over HTTPS.
- [x] Backend OpenAPI docs load over HTTPS (2026-08-03: /api/docs/swagger/).
- [x] Django migrations have run against the managed database.
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

- ~~Should the backend host be Vercel Services or Cloud Run for the first
  production-like MVP deployment?~~ Resolved (2026-08-03): Vercel Services.
- ~~Should the managed PostgreSQL provider be Neon or Aiven?~~ Resolved
  (2026-08-03): Neon free tier.
- What cold-start delay is acceptable for MVP testers?
- ~~Which provider should handle production email delivery?~~ Resolved
  (2026-08-04): Google SMTP with a Gmail app password.
- ~~Should production-like MVP testing use provider preview domains or custom
  domains?~~ Resolved (2026-08-03): provider preview domain
  `beacon-web3.vercel.app`.
- Where should Solana event monitoring and reconciliation run? (open, Task 8)

## Approval Gate

This plan should remain `Draft` until the manual blockers in Phase 1 are
resolved. Move to `Approved` only after the developer confirms provider choices,
account access, and the intended non-chain deployment scope.

Approved (2026-08-03): provider choices, account access, and the non-chain
deployment scope are confirmed; the deployed stack's health endpoint returns
`200 OK` over HTTPS. Tasks 7 and 8 remain blocked on their own manual blockers.
