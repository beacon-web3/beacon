# Backend Swagger OpenAPI Docs

Status: Completed

## Context

Beacon has a Django REST Framework backend with session-cookie authentication,
CSRF protection for browser sessions, public auth endpoints, protected default
API permissions, and a hand-maintained API contract in `docs/api/openapi.md`.

This plan adds generated OpenAPI documentation and public Swagger UI for the
backend. The goal is to make the API contract easier to inspect, test, and
consume without changing authentication behavior, product policy, tokenomics,
treasury assumptions, governance, staking, rewards, or Solana transaction
behavior.

Relevant specs and docs:

- `docs/api/openapi.md`
- `docs/architecture/system-design.md`
- `docs/development/testing.md`
- `apps/api/README.md`
- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/plans/0007-backend-auth-hardening.md`
- `docs/plans/0013-google-social-auth.md`

## User Decisions

- API docs should be publicly available in production.
- Use generated OpenAPI documentation rather than relying only on the
  hand-maintained Markdown API contract.

## Tooling Decision

- Use `drf-spectacular` as the OpenAPI generator for Django REST Framework.
- Prefer `drf-spectacular` over `drf-yasg` because it is actively maintained,
  supports OpenAPI 3.x well, integrates with DRF serializers/views, and provides
  Swagger UI and ReDoc views without hand-writing the whole schema.
- Keep the schema code-first with targeted annotations for endpoints where DRF
  cannot infer accurate request or response shapes.

## Guardrails

- Do not hide the schema or docs behind `DEBUG`; docs are intentionally public.
- Do not expose secrets, private environment values, provider tokens, internal
  stack traces, or admin-only operational details in schema descriptions or
  examples.
- Do not weaken existing DRF default authentication and permission settings.
- Do not change auth endpoint behavior while adding documentation.
- Do not document Beacon as an investment, passive yield, guaranteed-profit, or
  refundable-vote product.
- Keep Swagger/OpenAPI work separate from future endpoint additions.

## Public API Contract

The final public documentation routes should be:

- `GET /api/schema/`
  - Returns the generated OpenAPI schema for machine consumers.

- `GET /api/docs/swagger/`
  - Returns Swagger UI for human browsing and request inspection.

- `GET /api/docs/redoc/`
  - Returns ReDoc for a readable public reference view, unless implementation
    discovers a strong reason to omit it.

## Backend Tasks

- [x] Add and configure the OpenAPI dependency.
  - Acceptance: `drf-spectacular` is pinned in backend dependencies,
    `drf_spectacular` is installed in Django, and DRF uses
    `drf_spectacular.openapi.AutoSchema` as the default schema class.
  - Verify: `cd apps/api && .venv/bin/python manage.py check`.
  - Files likely touched: `apps/api/requirements.txt`, `apps/api/uv.lock`,
    `apps/api/beacon_api/settings.py`.
  - Dependencies: None.

- [x] Add public schema and documentation routes.
  - Acceptance: `/api/schema/`, `/api/docs/swagger/`, and `/api/docs/redoc/`
    are routed from the backend root URL configuration and are available without
    requiring an authenticated session.
  - Verify: Backend route tests return `200 OK` for each public docs endpoint.
  - Files likely touched: `apps/api/beacon_api/urls.py`, backend tests.
  - Dependencies: OpenAPI dependency configuration.

- [x] Configure production-safe schema metadata.
  - Acceptance: Schema metadata identifies the API as `Beacon API`, uses the
    backend package version or current project version, describes session-cookie
    authentication and CSRF expectations, and avoids operational secrets or
    private configuration details.
  - Verify: Inspect `/api/schema/` output and assert expected title/version in a
    focused test.
  - Files likely touched: `apps/api/beacon_api/settings.py`, backend tests.
  - Dependencies: OpenAPI dependency configuration.

- [x] Annotate existing auth API views for accurate generated docs.
  - Acceptance: Signup, login, logout, current account, email verification,
    password reset, social provider list, Google social start, and Google social
    callback endpoints show accurate request bodies, response envelopes, status
    codes, public/private access expectations, and CSRF/session notes where
    relevant.
  - Verify: Generate schema and review auth paths for expected request/response
    serializers and status codes.
  - Files likely touched: `apps/api/accounts/views.py`,
    `apps/api/accounts/google_social_views.py`, optional focused schema helpers.
  - Dependencies: Public schema route.

- [x] Add backend regression coverage for generated docs.
  - Acceptance: Tests cover schema availability, Swagger UI availability, ReDoc
    availability if included, public access without login, and configured schema
    class.
  - Verify: `cd apps/api && .venv/bin/pytest` or the focused backend test subset.
  - Files likely touched: `apps/api/tests/test_settings.py`,
    `apps/api/tests/test_smoke.py`, optional new `apps/api/tests/test_openapi.py`.
  - Dependencies: Routes and schema metadata.

## Documentation Tasks

- [x] Update API and backend setup documentation.
  - Acceptance: `docs/api/openapi.md` points users to the generated schema,
    Swagger UI, and ReDoc URLs; `apps/api/README.md` explains how to view public
    API docs locally and notes that docs are intended to remain available in
    production.
  - Verify: Documentation review confirms URLs and auth/CSRF notes match the
    implementation.
  - Files likely touched: `docs/api/openapi.md`, `apps/api/README.md`.
  - Dependencies: Final route names.

- [x] Update project tracking documentation.
  - Acceptance: `docs/plans/README.md` lists this plan, and `CHANGELOG.md`
    records the completed Swagger/OpenAPI documentation work once implemented.
  - Verify: Documentation review confirms status and changelog entry match the
    actual implementation state.
  - Files likely touched: `docs/plans/README.md`, `CHANGELOG.md`.
  - Dependencies: Implementation status.

## Acceptance Criteria

- `drf-spectacular` is the configured OpenAPI generator for DRF.
- `/api/schema/` returns the generated OpenAPI schema publicly.
- `/api/docs/swagger/` returns public Swagger UI in production and development.
- `/api/docs/redoc/` returns public ReDoc unless deliberately removed during
  implementation with a documented reason.
- Generated docs do not expose secrets, provider tokens, private env values, or
  misleading economic/product claims.
- Existing auth/session/CSRF behavior remains unchanged.
- Existing backend checks, Ruff checks, and relevant tests pass.
- API docs and backend README describe how to access generated docs.

## Verification

Completed implementation verification:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py spectacular --validate --file /var/folders/rh/ry4y28kd61gf4q10kvtktnpr0000gn/T/opencode/beacon-openapi.yaml
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest tests/test_openapi.py tests/test_settings.py
./scripts/test-postgres.sh
```

Full-suite verification remains the standard pre-merge check:

From `apps/api`:

```bash
.venv/bin/python manage.py check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
```

Manual local checks after starting the backend:

```text
GET http://localhost:8000/api/schema/
GET http://localhost:8000/api/docs/swagger/
GET http://localhost:8000/api/docs/redoc/
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Public docs expose operational details. | Medium | Keep descriptions focused on public API behavior and review schema output before launch. |
| Autogenerated API docs are inaccurate for custom `APIView` classes. | Medium | Add `@extend_schema` annotations and focused schema tests for auth endpoints. |
| Docs routes accidentally inherit authenticated defaults. | Low | Configure schema/docs views with public permissions and add unauthenticated route tests. |
| Dependency update causes lockfile or install drift. | Low | Pin the dependency, update the lockfile through the backend package workflow, and run backend checks/tests. |

## Open Questions

- None. Public production docs and `drf-spectacular` are accepted for this plan.
