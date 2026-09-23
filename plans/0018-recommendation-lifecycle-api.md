# Plan: Recommendation Lifecycle API

## Status

Draft

## Linked Specs

- `docs/product/mvp.md` — MVP scope, minimum stake (0.2 SOL), fixed support (0.01 SOL), badge tiers
- `docs/product/user-stories.md` — Curator, Reactivator, Supporter, Early Supporter, Reader stories
- `docs/architecture/system-design.md` — Three-layer architecture, backend as cache not source of truth
- `docs/api/openapi.md` — Existing auth API surface, session-cookie pattern
- `docs/decisions/0011-hybrid-recommendation-lifecycle.md` — One canonical page, permanent discoverer credit, one active cycle
- `docs/tokenomics/rewards.md` — Badge tiers, milestone model, treasury split
- `apps/api/recommendations/models.py` — 9 Django models with constraints and indexes

## Objective

Implement the REST API surface for Beacon's recommendation lifecycle: creating and
listing canonical book recommendations, activating and reactivating recommendations,
supporting with fixed 0.01 SOL contributions, bookmarking, following curators,
viewing badges and reputation, and filing duplicate reports. The backend owns
product state and returns Solana transaction construction hints; the client signs
and submits transactions via the SDK.

## Scope

In scope:

- 25 API endpoints across 7 resource groups (Recommendations, Stake, Bookmarks,
  Curator Follows, Badges, Reputation, Duplicate Reports).
- Serializers, views, URL routing, throttle classes, and permission classes for
  all endpoints.
- Pagination (page-number, default 20, max 100) and filtering for list endpoints.
- Rate limiting for all mutating endpoints.
- Test coverage for every endpoint.
- Response format definitions including Solana transaction hints.

Out of scope:

- Actual Solana transaction signing, submission, or staking flows.
- Final reward split formulas or reputation aggregation logic.
- Frontend UI for these endpoints.
- A governance token.
- Community moderation for duplicate reports (admin-only via Django admin for MVP).

## Dependencies

- Product decisions: Plan 0016 data model is complete and migrated (0001_initial.py exists).
- Technical decisions: `docs/decisions/0011-hybrid-recommendation-lifecycle.md` accepted.
- Open questions: Reputation aggregation formula deferred (store raw events only).

## API Design Principles

- All endpoints live under `/api/`.
- Session-cookie authentication with CSRF for browser clients.
- RESTful resource-oriented design with noun-based paths.
- JSON request and response bodies.
- Page-number pagination for list endpoints (default 20, max 100).
- Filtering via query parameters.
- Idempotency keys for mutating operations that create records.
- Rate limiting on all mutating endpoints.
- Backend returns Solana transaction hints inline; client signs and submits via SDK.

## Endpoint Catalog

### Recommendations

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `GET` | `/api/recommendations/` | List canonical recommendations with filtering and pagination. | Optional | Yes |
| `POST` | `/api/recommendations/` | Create a new book recommendation (candidate or canonical). | Required | Yes (client-generated idempotency key) |
| `GET` | `/api/recommendations/{id}/` | Retrieve a single recommendation. | Optional | Yes |
| `PATCH` | `/api/recommendations/{id}/` | Update recommendation metadata (creator only, before activation). | Required | No |
| `POST` | `/api/recommendations/{id}/recommend/` | Activate (recommend) an inactive recommendation with recommender stake. | Required | Yes |
| `POST` | `/api/recommendations/{id}/reactivate/` | Reactivate an inactive recommendation with recommender stake. | Required | Yes |
| `POST` | `/api/recommendations/{id}/support/` | Prepare a support contribution: validate eligibility and return Solana transaction hints. No record is created. | Required | Yes |
| `POST` | `/api/recommendations/{id}/support/confirm/` | Confirm an on-chain support transaction, creating the `Support` record. Idempotent (client-generated idempotency key). | Required | Yes |
| `GET` | `/api/recommendations/{id}/supports/` | List supports for a recommendation. | Optional | Yes |

#### Filtering and Pagination

`GET /api/recommendations/` supports:

- `?status=ACTIVE|INACTIVE` — filter by lifecycle status.
- `?page_type=STANDALONE_WORK|RECOGNIZED_SERIES` — filter by page type.
- `?category={slug}` — filter by category.
- `?duplicate_risk_status=LOW_RISK|HIGH_RISK|NEEDS_REVIEW` — filter by risk.
- `?review_status=NOT_REQUIRED|PENDING|APPROVED|REJECTED` — filter by review.
- `?creator={username}` — filter by creator.
- `?is_canonical=true|false` — filter by canonical status.
- `?search={query}` — search by title or author names (minimum 3 characters).
- `?ordering=-support_count|created_at|-created_at` — sort order.
- `?page={n}&page_size={n}` — page-number pagination (default page_size=20,
  max=100).

Search requires a minimum query length of 3 characters. Shorter queries return
an empty results set (not an error) to avoid expensive full-table scans.

### Recommender Stake

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/recommendations/{id}/stake/` | Add locked SOL to an existing recommender position. | Required | Yes |
| `DELETE` | `/api/recommendations/{id}/stake/` | Reclaim all locked SOL from an active recommender position. | Required | No |
| `GET` | `/api/recommendations/{id}/stake/history/` | List recommender participant history for a recommendation. | Optional | Yes |

#### Stake Validation Rules

- `POST /stake/` is top-up only: it requires an existing
  `RecommenderParticipant` for the caller on that recommendation (400 if
  none). Creating or activating a position happens exclusively through
  `POST /recommend/` (first cycle) and `POST /reactivate/` (later cycles).
- Minimum activation/reactivation stake (recommend/reactivate):
  200,000,000 lamports (0.2 SOL).
- Minimum top-up above existing qualifying balance: 50,000,000 lamports
  (0.05 SOL).
- No maximum deposit cap.
- Withdrawal that would leave balance between 1 and 199,999,999 lamports
  is rejected (must withdraw to 0 or keep above 200M).
- Stake operations return Solana transaction construction data for the client
  to sign and submit.

### Bookmarks

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/recommendations/{id}/bookmark/` | Bookmark a recommendation. | Required | Yes |
| `DELETE` | `/api/recommendations/{id}/bookmark/` | Remove bookmark. | Required | No |
| `GET` | `/api/accounts/me/bookmarks/` | List current user's bookmarked recommendations. | Required | Yes |

### Curator Follows

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/accounts/{username}/follow/` | Follow a curator. | Required | Yes |
| `DELETE` | `/api/accounts/{username}/follow/` | Unfollow a curator. | Required | No |
| `GET` | `/api/accounts/{username}/followers/` | List followers of a curator. | Optional | Yes |
| `GET` | `/api/accounts/{username}/following/` | List curators a user follows. | Optional | Yes |

Self-follow is rejected at the application level (enforced by
`curatorfollow_no_self_follow` constraint).

### Badges

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `GET` | `/api/recommendations/{id}/badges/` | List badges for a recommendation. | Optional | Yes |
| `GET` | `/api/accounts/{username}/badges/` | List badges earned by a user. | Optional | Yes |

Badge tiers (draft, from `docs/tokenomics/rewards.md`):

| Tier | Milestone |
|------|-----------|
| BRONZE | 100 supporters |
| SILVER | 1,000 supporters |
| GOLD | 10,000 supporters |
| DIAMOND | 100,000 supporters |

### Reputation

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `GET` | `/api/accounts/{username}/reputation/` | Read reputation event history for a user. | Optional | Yes |
| `GET` | `/api/accounts/{username}/profile/` | Read public profile summary (display name, reputation score, badge count). | Optional | Yes |

The exact reputation aggregation formula is not implemented. The API returns
the raw event history and the `Account.reputation_score` field. A future
aggregation process will compute the score.

### Duplicate Reports

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/recommendations/{id}/report-duplicate/` | File a duplicate report against a recommendation. | Required | Yes |
| `GET` | `/api/recommendations/{id}/duplicate-reports/` | List duplicate reports for a recommendation (admin only). | Required (admin) | Yes |

#### Duplicate Report Request Body

```json
{
  "suspected_duplicate_of": 1 (optional — integer id of the suspected original recommendation),
  "reason": "string (optional — free-text explanation)"
}
```

## Solana Transaction Separation

Backend product state endpoints return data and validation. Solana transaction
construction and signing happen on the client side using the SDK. The backend
provides:

- Transaction construction hints (program accounts, PDA seeds, required
  accounts) as part of response payloads.
- On-chain transaction signature recording after the client submits and
  confirms a transaction, via `POST /api/recommendations/{id}/support/confirm/`
  for supports. Recommender stake on-chain fields remain nullable in MVP
  (recorded by future on-chain indexing/sync work).
- Indexing of on-chain state as cache fields (not source of truth for custody).

The backend does not:

- Sign Solana transactions.
- Hold private keys.
- Submit transactions to the Solana network.
- Act as source of truth for on-chain custody or fund movement.

## Permissions

| Resource | Read | Create | Update | Delete |
|----------|------|--------|--------|--------|
| Recommendation | Public (summary fields) / Authenticated (full fields) | Authenticated | Creator only | N/A |
| Recommender Stake | Public (summary) / Authenticated (full) | Authenticated (active position holder) | N/A | Creator (reclaim) |
| Support | Public | Authenticated | N/A | N/A |
| Bookmark | Owner only | Owner | N/A | Owner |
| Curator Follow | Public | Owner | N/A | Owner |
| Badge | Public | N/A (system-generated) | N/A | N/A |
| Reputation Event | Public | N/A (system-generated) | N/A | N/A |
| Duplicate Report | Admin | Authenticated | N/A | N/A |

### Serializer Levels

Two serializer levels prevent leaking internal fields to unauthenticated users:

- **Summary serializer** (list endpoints, public): `id`, `title`, `author_names`,
  `page_type`, `status`, `support_count`, `category`, `created_at`.
  Excludes: `current_recommender`, `on_chain_*` fields, `duplicate_risk_status`,
  `review_status`, `creator`.
- **Detail serializer** (detail endpoints, authenticated): All model fields
  including `current_recommender`, `on_chain_*`, `duplicate_risk_status`,
  `review_status`, `creator`. Unauthenticated requests to detail endpoints
  receive the summary serializer.

## Rate Limiting

| Endpoint | Throttle | Rate |
|----------|----------|------|
| `POST /api/recommendations/` | RecommendationCreateThrottle | 10/min |
| `PATCH /api/recommendations/{id}/` | RecommendationUpdateThrottle | 10/min |
| `POST /api/recommendations/{id}/recommend/` | RecommendationActThrottle | 5/min |
| `POST /api/recommendations/{id}/reactivate/` | RecommendationActThrottle | 5/min |
| `POST /api/recommendations/{id}/support/`, `.../support/confirm/` | RecommendationSupportThrottle | 20/min |
| `POST /api/recommendations/{id}/stake/` | RecommendationStakeThrottle | 5/min |
| `DELETE /api/recommendations/{id}/stake/` | RecommendationStakeThrottle | 5/min |
| `POST /api/recommendations/{id}/bookmark/` | RecommendationBookmarkThrottle | 10/min |
| `POST /api/accounts/{username}/follow/` | RecommendationFollowThrottle | 10/min |
| `POST /api/recommendations/{id}/report-duplicate/` | RecommendationDuplicateThrottle | 5/min |
| List endpoints | RecommendationReadThrottle | 60/min |

Each throttle class is a `SimpleRateThrottle` subclass whose `scope` selects a
rate from `settings.RECOMMENDATION_THROTTLE_RATES` (one bucket per endpoint
group, so traffic on one endpoint does not exhaust another).

Throttle rates are configured in `settings.RECOMMENDATION_THROTTLE_RATES`
following the same pattern as `AUTH_THROTTLE_RATES`.

## Idempotency

Mutating `POST` endpoints that create records are idempotent via a
client-generated `Idempotency-Key` header (matching the `Yes` column in the
endpoint catalog): `POST /api/recommendations/`, recommend, reactivate,
`.../support/confirm/`, stake, bookmark, follow, and report-duplicate.

Behavior:

- The backend stores a per-user SHA-256 hash of the key scoped to
  `(user, method, path, key)` — raw keys are never persisted — together with
  the successful response (status + body).
- Replaying the same `(user, method, path, key)` returns the stored response
  instead of re-executing the mutation — critical for confirm-after-sign
  retries.
- A concurrent in-flight request with the same key returns `409` while the
  first request is still processing.
- Non-2xx responses are not cached; the client may retry with a fresh key.
- A stale in-flight record (older than 60s, e.g. from a crashed process) may
  be taken over; the takeover re-reads the row under a row lock so concurrent
  takers cannot both execute the mutation.
- Cached responses expire after 1 hour (`IDEMPOTENCY_TTL_SECONDS`); expired
  records are re-executed and opportunistically pruned per user.

## State Transitions

### Support During INACTIVE

When a support is confirmed against an INACTIVE recommendation
(`POST .../support/confirm/`):

1. Create the `Support` record with the next `supporter_number` (computed
   inside the locked block) and the client's on-chain transaction signature
   (required by `Support.clean()`).
2. Increment `BookRecommendation.support_count`.
3. Set `BookRecommendation.last_support_at` to now.
4. If the recommendation has an existing `RecommenderParticipant` with
   `is_active=True`: set `BookRecommendation.status` to `ACTIVE`,
   set `activated_at` to now, clear `deactivated_at`.
5. If no active `RecommenderParticipant` exists: the recommendation stays
   INACTIVE (support is recorded but the cycle is not activated — a
   recommender must stake to activate).

All four steps run inside a single `transaction.atomic()` block with
`select_for_update()` on the `BookRecommendation` row. The prepare call
(`POST .../support/`) performs no writes.

## Response Formats

### Recommendation Summary (list, public)

```json
{
  "results": [
    {
      "id": 1,
      "title": "Dune",
      "author_names": "Frank Herbert",
      "page_type": "STANDALONE_WORK",
      "status": "ACTIVE",
      "support_count": 42,
      "category": { "id": 1, "name": "Science Fiction", "slug": "sci-fi" },
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "count": 150,
  "page": 1,
  "page_size": 20
}
```

### Recommendation Detail (authenticated)

```json
{
  "recommendation": {
    "id": 1,
    "title": "Dune",
    "author_names": "Frank Herbert",
    "page_type": "STANDALONE_WORK",
    "status": "ACTIVE",
    "is_canonical": true,
    "support_count": 42,
    "category": { "id": 1, "name": "Science Fiction", "slug": "sci-fi" },
    "creator": { "username": "frank_h", "display_name": "Frank H." },
    "current_recommender": { "username": "frank_h" },
    "recommendation_cycle_number": 1,
    "activated_at": "2026-01-15T10:00:00Z",
    "duplicate_risk_status": "LOW_RISK",
    "review_status": "APPROVED",
    "on_chain_program_account": "Prog...",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-20T14:30:00Z",
    "solana_hints": {
      "program_id": "...",
      "recommendation_account": "...",
      "pda_seeds": ["recommendation", "1"]
    }
  }
}
```

### Support Prepare Response (with Solana hints)

`POST /api/recommendations/{id}/support/` validates eligibility and returns a
quote plus transaction construction hints. No record is created.

```json
{
  "support_quote": {
    "supporter_number": 43,
    "amount_lamports": 10000000,
    "recommendation_cycle_number": 1
  },
  "solana_hints": {
    "program_id": "...",
    "support_account_pda": "...",
    "recommendation_account": "...",
    "amount_lamports": 10000000,
    "pda_seeds": ["support", "1", "43"]
  }
}
```

The quoted `supporter_number` is informational for PDA construction. The
confirm response returns the authoritative number; if it differs (race), the
client re-derives the PDA and re-signs.

### Support Confirm Request

`POST /api/recommendations/{id}/support/confirm/` records the on-chain
signature and creates the `Support` record.

```json
{
  "transaction_signature": "base58 signature, 87-88 chars",
  "on_chain_support_account": "base58 account, 64 chars (optional)"
}
```

### Support Confirm Response

```json
{
  "support": {
    "id": 1,
    "supporter_number": 43,
    "amount_lamports": 10000000,
    "recommendation_cycle_number": 1,
    "created_at": "2026-01-20T14:30:00Z"
  }
}
```

### Recommend/Reactivate Response (with Solana hints)

```json
{
  "recommendation": { "...full detail fields..." },
  "recommender_participant": {
    "id": 1,
    "locked_amount_lamports": 200000000,
    "reactivation_number": 1,
    "is_active": true
  },
  "solana_hints": {
    "program_id": "...",
    "stake_account_pda": "...",
    "recommendation_account": "...",
    "amount_lamports": 200000000,
    "pda_seeds": ["stake", "1", "user_wallet"]
  }
}
```

### Error Response (DRF default)

```json
{
  "detail": "Not authenticated."
}
```

Validation errors follow DRF's default format:

```json
{
  "title": ["This field is required."],
  "page_type": ["'INVALID' is not a valid choice."]
}
```

## Phases

### Phase 1: Foundation (completed)

#### Task 1: Recommendation serializers

Create `apps/api/recommendations/serializers.py` with all serializers needed
across the recommendation lifecycle endpoints. This includes input serializers
(plain `serializers.Serializer`), output serializers (`ModelSerializer` with
`read_only_fields`), and envelope wrappers.

Input serializers: `CreateRecommendationSerializer`,
`UpdateRecommendationSerializer`, `RecommendSerializer` (activate),
`ReactivateSerializer`, `SupportCreateSerializer`, `SupportConfirmSerializer`,
`StakeAddSerializer`,
`BookmarkSerializer`, `CuratorFollowSerializer`,
`DuplicateReportCreateSerializer`.

Output serializers: `RecommendationSummarySerializer` (public list fields),
`RecommendationDetailSerializer` (full fields for authenticated users),
`RecommenderParticipantSerializer`, `SupportReadSerializer`,
`BookmarkReadSerializer`, `CuratorFollowSerializer` (read),
`BadgeSerializer`, `ReputationEventSerializer`,
`DuplicateReportReadSerializer`, `ProfileSerializer`.

Envelope wrappers: `RecommendationEnvelopeSerializer`,
`RecommendationListEnvelopeSerializer`, `SupportEnvelopeSerializer`,
`DetailEnvelopeSerializer`.

Acceptance criteria:

- [x] Every endpoint in the catalog has a corresponding input and output serializer.
- [x] Summary serializer excludes `current_recommender`, `on_chain_*`,
  `duplicate_risk_status`, `review_status`, `creator`.
- [x] Detail serializer includes all model fields.
- [x] Input serializers validate per the stake validation rules (0.2 SOL
  minimum, 0.05 SOL top-up minimum, no dust balance).
- [x] `SupportCreateSerializer` input has no user-provided amount (fixed at
  10,000,000 lamports).
- [x] `SupportConfirmSerializer` validates `transaction_signature` (required,
  valid base58 Ed25519 signature, 87-88 chars) and optional
  `on_chain_support_account`.
- [x] `DuplicateReportCreateSerializer` input accepts optional `suspected_duplicate_of`
  (integer recommendation id) and optional `reason` (string).
- [x] `CreateRecommendationSerializer` writes `title_normalized` /
  `author_names_normalized` as lowercased copies of `title` / `author_names`
  (models keep them in sync via serializers per Plan 0018).

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_serializers.py -v`
- [x] `python manage.py check` passes.

Files likely touched:

- `apps/api/recommendations/serializers.py` (new)
- `apps/api/tests/recommendations/test_serializers.py` (new)

Dependencies: None.

Estimated scope: Large (5+ serializers, 200+ lines).

#### Task 2: URL routing, throttle classes, and idempotency infrastructure

Create `apps/api/recommendations/urls.py` with all URL patterns for the
`/api/recommendations/...` endpoints from the catalog. Create
`apps/api/accounts/account_urls.py` with URL patterns for the
`/api/accounts/...` endpoints (bookmarks-me, follows, badges, reputation,
profile). Create `apps/api/recommendations/throttles.py` with per-endpoint `SimpleRateThrottle`
subclasses (`RecommendationCreateThrottle`, `RecommendationActThrottle`,
`RecommendationSupportThrottle`, `RecommendationStakeThrottle`,
`RecommendationBookmarkThrottle`, `RecommendationFollowThrottle`,
`RecommendationDuplicateThrottle`, `RecommendationReadThrottle`) following the
`AuthRateThrottle` pattern. Register both URL confs in the root `urls.py`.

Create the idempotency infrastructure: a small `apps/api/common/` app with an
`IdempotencyRecord` model and an `IdempotencyKeyMixin` view mixin. The model
stores a per-user SHA-256 hash of the client's `Idempotency-Key` header (raw
keys are never persisted) together with the successful response. The mixin
returns the cached response on replay, returns `409` for a concurrent in-flight
request with the same key, and does not cache non-2xx responses.

Acceptance criteria:

- [x] All 25 endpoints from the catalog have URL patterns
  (`recommendations/urls.py` + `accounts/account_urls.py`).
- [x] URLs use `path()` with trailing slashes and named URLs.
- [x] Root `urls.py` includes `path("api/", include("recommendations.urls"))`
  and `path("api/accounts/", include("accounts.account_urls"))`.
- [x] Existing auth endpoints remain at `/api/auth/` (no regressions).
- [x] `RecommendationRateThrottle` subclasses `SimpleRateThrottle`; each
  per-endpoint throttle subclass reads its rate from
  `settings.RECOMMENDATION_THROTTLE_RATES`.
- [x] Mutating views reference their per-endpoint throttle classes; public
  read views use `RecommendationReadThrottle`.
- [x] `IdempotencyRecord` model has a migration and is registered in
  `INSTALLED_APPS` as `common` (following the existing app naming convention).
- [x] `Idempotency-Key` header is honored on mutating POST endpoints listed in
  the Idempotency section; replay returns the stored response, in-flight
  concurrency returns 409, keys are stored hashed.

Verification:

- [x] `python manage.py check` passes.
- [x] `python manage.py showmigrations recommendations` shows migration applied.
- [x] Tests pass: `pytest apps/api/tests/recommendations/test_urls.py -v`
- [x] Tests pass: `pytest apps/api/tests/common/test_idempotency.py -v`

Files likely touched:

- `apps/api/recommendations/urls.py` (new)
- `apps/api/accounts/account_urls.py` (new)
- `apps/api/recommendations/throttles.py` (new)
- `apps/api/common/__init__.py` (new)
- `apps/api/common/apps.py` (new)
- `apps/api/common/models.py` (new — `IdempotencyRecord`)
- `apps/api/common/idempotency.py` (new — `IdempotencyKeyMixin`)
- `apps/api/common/migrations/0001_initial.py` (generated)
- `apps/api/beacon_api/urls.py` (add both includes)
- `apps/api/beacon_api/settings.py` (add `RECOMMENDATION_THROTTLE_RATES`,
  register `common` app)
- `apps/api/tests/recommendations/test_urls.py` (new)
- `apps/api/tests/common/test_idempotency.py` (new)

Dependencies: Task 1.

Estimated scope: Medium.

#### Task 3: Recommendation model factories

Extend `apps/api/tests/recommendations/factories.py` to cover all 9
recommendation models. Factories already exist for `Category`,
`BookRecommendation`, `DuplicateReport`, `RecommenderParticipant`, `Support`,
`Bookmark`, `CuratorFollow`, `Badge`, and `ReputationEvent`; extend or adjust
them so every factory creates a valid instance with sensible defaults and
supports overrides for critical fields (status, amounts, etc.).

Acceptance criteria:

- [x] Each factory creates a valid model instance with sensible defaults.
- [x] Factories support overrides for all critical fields (status, amounts, etc.).
- [x] `BookRecommendationFactory` default status is INACTIVE.
- [x] `SupportFactory` default `amount_lamports` is 10,000,000.
- [x] `RecommenderParticipantFactory` default `locked_amount_lamports` is
  200,000,000.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_models.py -v`

Files likely touched:

- `apps/api/tests/recommendations/factories.py` (extend)
- `apps/api/tests/recommendations/test_models.py` (extend)

Dependencies: Task 1.

Estimated scope: Small.

### Checkpoint: Foundation

- [x] All serializers validate correctly against model constraints.
- [x] All URL patterns resolve.
- [x] `python manage.py check` passes.
- [x] `manage.py test` passes for serializer and URL tests.

### Phase 2: Recommendation CRUD (completed)

#### Task 4: Recommendation list and detail endpoints

Implement `GET /api/recommendations/` (list with filtering and pagination)
and `GET /api/recommendations/{id}/` (detail). List endpoint uses summary
serializer (public); detail endpoint uses detail serializer for authenticated
users and summary serializer for anonymous.

Acceptance criteria:

- [x] `GET /recommendations/` returns paginated list with summary fields.
- [x] All filter parameters work: `status`, `page_type`, `category`,
  `duplicate_risk_status`, `review_status`, `creator`, `is_canonical`,
  `search`, `ordering`.
- [x] `search` requires minimum 3 characters; shorter queries return empty
  results.
- [x] `page_size` defaults to 20, max 100.
- [x] `GET /recommendations/{id}/` returns detail fields for authenticated
  users.
- [x] `GET /recommendations/{id}/` returns summary fields for anonymous users.
- [x] `GET /recommendations/{id}/` returns 404 for nonexistent IDs.
- [x] Every view has `@extend_schema` documentation.
- [x] `GET /recommendations/` applies the public read throttle (60/min);
  `POST /recommendations/` (Phase 2 create handler) uses the create throttle
  (10/min) via `get_throttles()`, which switches on `request.method`.
- [x] N+1 note: list/detail querysets must use `select_related` /
  `prefetch_related` for the nested summary/detail serializers (`category`,
  `creator`, `current_recommender`) to avoid per-row queries.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_recommendation_list.py -v`
- [x] Manual check: `curl` list and detail endpoints return expected shapes.

Files likely touched:

- `apps/api/recommendations/views.py` (new — `RecommendationListView`,
  `RecommendationDetailView`)
- `apps/api/recommendations/serializers.py` (may need adjustments)
- `apps/api/tests/recommendations/test_recommendation_list.py` (new)

Dependencies: Tasks 1, 2, 3.

Estimated scope: Large.

#### Task 5: Recommendation create and update endpoints

Implement `POST /api/recommendations/` (create) and
`PATCH /api/recommendations/{id}/` (update metadata). Create endpoint
requires authentication. Update is restricted to the creator and only allowed
before activation (status is INACTIVE and `recommendation_cycle_number == 0`).

Acceptance criteria:

- [x] `POST /recommendations/` creates a recommendation with status INACTIVE.
- [x] `POST /recommendations/` requires authentication (403 for anonymous).
- [x] `POST /recommendations/` validates unique canonical constraint
  (title + author + page_type).
- [x] `PATCH /recommendations/{id}/` updates metadata fields only.
- [x] `PATCH /recommendations/{id}/` returns 403 for non-creators.
- [x] `PATCH /recommendations/{id}/` returns 400 if recommendation is already
  active (`recommendation_cycle_number > 0`).
- [x] `POST /recommendations/` is idempotent (client-generated idempotency key).
- [x] Every view has `@extend_schema` documentation.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_recommendation_create.py -v`
- [x] Manual check: create, update, and verify permissions.

Files likely touched:

- `apps/api/recommendations/views.py` (add `RecommendationCreateView`,
  `RecommendationUpdateView`)
- `apps/api/recommendations/serializers.py` (may need adjustments)
- `apps/api/tests/recommendations/test_recommendation_create.py` (new)

Dependencies: Task 4.

Estimated scope: Medium.

### Checkpoint: Recommendation CRUD

- [x] Create, read, update, list, filter, and paginate work end-to-end.
- [x] Permission checks pass: creator-only update, auth-only create.
- [x] Search with < 3 characters returns empty results.
- [x] OpenAPI schema generates correctly for recommendation endpoints.

### Phase 3: Activation and Support (completed)

#### Task 6: Recommend (activate) endpoint

Implement `POST /api/recommendations/{id}/recommend/` which activates an
inactive recommendation for the first time. Creates a `RecommenderParticipant`
with `is_active=True`, sets `current_recommender`, increments
`recommendation_cycle_number`, sets `status` to ACTIVE, and records
`activated_at`. Returns Solana transaction hints inline.

Acceptance criteria:

- [x] `POST /recommendations/{id}/recommend/` creates a `RecommenderParticipant`.
- [x] `BookRecommendation.status` changes from INACTIVE to ACTIVE.
- [x] `BookRecommendation.current_recommender` is set to the requesting user.
- [x] `BookRecommendation.recommendation_cycle_number` increments.
- [x] `BookRecommendation.activated_at` is set.
- [x] Returns 400 if recommendation is already ACTIVE.
- [x] Returns 400 if user already has an active participant on this recommendation.
- [x] Uses `select_for_update()` on `BookRecommendation` for concurrency safety.
- [x] Response includes `solana_hints` with program ID, PDA seeds, amount.
- [x] Operation runs inside `transaction.atomic()`.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_recommend.py -v`
- [x] Concurrency test: two simultaneous requests, only one succeeds.

Files likely touched:

- `apps/api/recommendations/views.py` (add `RecommendView`)
- `apps/api/tests/recommendations/test_recommend.py` (new)

Dependencies: Task 5.

Estimated scope: Medium.

#### Task 7: Reactivate endpoint

Implement `POST /api/recommendations/{id}/reactivate/` which reactivates
an inactive recommendation that has a previous cycle. Creates a new
`RecommenderParticipant` (incrementing `reactivation_number`), updates
`current_recommender`, increments `recommendation_cycle_number`, sets
`status` to ACTIVE, clears `deactivated_at`. Returns Solana transaction hints.

Acceptance criteria:

- [x] `POST /recommendations/{id}/reactivate/` creates a new
  `RecommenderParticipant` with incremented `reactivation_number`.
- [x] `BookRecommendation.status` changes to ACTIVE.
- [x] `BookRecommendation.deactivated_at` is cleared.
- [x] Returns 400 if recommendation is already ACTIVE.
- [x] Returns 400 if `recommendation_cycle_number == 0` (use recommend instead).
- [x] Uses `select_for_update()` on `BookRecommendation`.
- [x] Response includes `solana_hints`.
- [x] Runs inside `transaction.atomic()`.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_reactivate.py -v`

Dependencies: Task 6.

Estimated scope: Medium.

#### Task 8: Support prepare and confirm endpoints

Implement `POST /api/recommendations/{id}/support/` (prepare) and
`POST /api/recommendations/{id}/support/confirm/` (confirm). A support is
two-phase: the prepare call validates eligibility and returns Solana
transaction construction hints (no record is created — `Support.clean()`
requires the on-chain signature); after the client signs and submits on-chain,
the confirm call records the transaction signature and creates the `Support`
record.

Prepare:

- Validates authentication and that the user is not already a supporter.
- Returns a support quote (anticipated next `supporter_number`, cycle number,
  fixed 10,000,000 lamport amount) plus `solana_hints`.
- Performs no database writes.

Confirm (inside `transaction.atomic()` with `select_for_update()` on the
`BookRecommendation` row):

- Re-checks the one-support-per-supporter rule (409 on duplicate).
- Creates the `Support` record with the next `supporter_number`, the fixed
  amount, the current `recommendation_cycle_number`, and the client's
  `transaction_signature` (satisfying `Support.clean()`).
- Increments `BookRecommendation.support_count`, updates `last_support_at`.
- Applies the Support-During-INACTIVE state transition (see State Transitions).
- Idempotent via the `Idempotency-Key` header (replay returns the same support).

Acceptance criteria:

- [x] `POST /recommendations/{id}/support/` returns a quote and hints without
  persisting anything (`support_count` unchanged, no `Support` rows).
- [x] `POST /recommendations/{id}/support/` returns 409 if the user is already
  a supporter.
- [x] `POST /recommendations/{id}/support/confirm/` creates a `Support` record
  with `amount_lamports=10_000_000`, the given `transaction_signature`, and
  the correct next `supporter_number`; `full_clean()` passes.
- [x] `POST /recommendations/{id}/support/confirm/` requires a valid base58
  Ed25519 `transaction_signature` (87-88 chars; 400 otherwise).
- [x] `supporter_number` is sequenced atomically (no duplicates under
  concurrency).
- [x] `BookRecommendation.support_count` is incremented and `last_support_at`
  is updated at confirm.
- [x] Support confirm during INACTIVE with active recommender transitions to
  ACTIVE; without active recommender stays INACTIVE.
- [x] Replaying the same confirm request (same idempotency key) returns the
  stored support response and does not create a second record.
- [x] Response includes `solana_hints` on prepare.
- [x] Runs inside `transaction.atomic()`.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_support.py -v`
- [x] Concurrency test: simultaneous confirms get different `supporter_number`.
- [x] Idempotency replay test for confirm.

Files likely touched:

- `apps/api/recommendations/views.py` (add `SupportView`, `SupportConfirmView`)
- `apps/api/tests/recommendations/test_support.py` (new)

Dependencies: Task 5.

Estimated scope: Large.

#### Task 9: Support list endpoint

Implement `GET /api/recommendations/{id}/supports/` which lists supports
for a recommendation, ordered by `supporter_number`.

Acceptance criteria:

- [x] Returns paginated list of supports.
- [x] Supports are ordered by `supporter_number` ascending.
- [x] Each support includes `supporter_number`, `amount_lamports`,
  `recommendation_cycle_number`, `created_at`.
- [x] Supports are publicly readable.
- [x] Returns 404 for nonexistent recommendation.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_support_list.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `SupportListView`)
- `apps/api/tests/recommendations/test_support_list.py` (new)

Dependencies: Task 8.

Estimated scope: Small.

### Checkpoint: Activation and Support

- [x] Recommend, reactivate, and support endpoints work end-to-end.
- [x] Support during INACTIVE correctly transitions to ACTIVE when applicable.
- [x] `supporter_number` is unique per recommendation (no races).
- [x] Solana hints are included in all mutating responses.
- [x] Concurrency tests pass for supporter_number and status transitions.

### Phase 4: Auxiliary Endpoints (completed)

#### Task 10: Bookmark endpoints

Implement `POST /api/recommendations/{id}/bookmark/`,
`DELETE /api/recommendations/{id}/bookmark/`, and
`GET /api/accounts/me/bookmarks/`. Toggle pattern (POST to add, DELETE to remove).
`UserBookmarksView` lives in `recommendations/views.py`; its URL is registered in
`accounts/account_urls.py` since the path is under `/accounts/`.

Acceptance criteria:

- [x] `POST /recommendations/{id}/bookmark/` creates a bookmark (201).
- [x] `POST /recommendations/{id}/bookmark/` returns 409 if already bookmarked.
- [x] `DELETE /recommendations/{id}/bookmark/` removes bookmark (204).
- [x] `DELETE /recommendations/{id}/bookmark/` returns 404 if not bookmarked.
- [x] `GET /accounts/me/bookmarks/` returns current user's bookmarks.
- [x] All bookmark endpoints require authentication.
- [x] Each view has `@extend_schema` documentation.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_bookmarks.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `BookmarkView`,
  `UserBookmarksView`)
- `apps/api/accounts/account_urls.py` (add bookmark URL patterns)
- `apps/api/tests/recommendations/test_bookmarks.py` (new)

Dependencies: Task 5.

Estimated scope: Medium.

#### Task 11: Curator follow endpoints

Implement `POST /api/accounts/{username}/follow/`,
`DELETE /api/accounts/{username}/follow/`,
`GET /api/accounts/{username}/followers/`, and
`GET /api/accounts/{username}/following/`. These live in the accounts app
since they're under `/accounts/`, with URL patterns in
`accounts/account_urls.py` (not the existing `accounts/urls.py` auth conf).

Acceptance criteria:

- [x] `POST /accounts/{username}/follow/` creates a follow (201).
- [x] `POST /accounts/{username}/follow/` returns 400 for self-follow.
- [x] `POST /accounts/{username}/follow/` returns 409 if already following.
- [x] `DELETE /accounts/{username}/follow/` removes follow (204).
- [x] `GET /accounts/{username}/followers/` returns paginated follower list.
- [x] `GET /accounts/{username}/following/` returns paginated following list.
- [x] Follow/unfollow require authentication.
- [x] Follower/following lists are publicly readable.

Verification:

- [x] Tests pass: `pytest apps/api/tests/accounts/test_follow.py -v`

Files likely touched:

- `apps/api/accounts/views.py` (add follow views)
- `apps/api/accounts/account_urls.py` (add follow URL patterns)
- `apps/api/tests/accounts/test_follow.py` (new)

Dependencies: Task 3.

Estimated scope: Medium.

#### Task 12: Badge endpoints

Implement `GET /api/recommendations/{id}/badges/` and
`GET /api/accounts/{username}/badges/`. Both are read-only, publicly accessible.
The recommendation-scoped route lives in `recommendations/urls.py`; the
account-scoped route is registered in `accounts/account_urls.py`.

Acceptance criteria:

- [x] `GET /recommendations/{id}/badges/` returns badges for a recommendation.
- [x] `GET /accounts/{username}/badges/` returns badges earned by a user.
- [x] Badge response includes `tier`, `earned_at`, and `recommendation` fields.
- [x] Both endpoints are publicly readable.
- [x] Returns empty list if no badges earned.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_badges.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add badge views)
- `apps/api/accounts/account_urls.py` (add account-scoped badge route)
- `apps/api/tests/recommendations/test_badges.py` (new)

Dependencies: Task 3.

Estimated scope: Small.

#### Task 13: Reputation and profile endpoints

Implement `GET /api/accounts/{username}/reputation/` and
`GET /api/accounts/{username}/profile/`. Both are publicly readable, with
URL patterns in `accounts/account_urls.py`.

Acceptance criteria:

- [x] `GET /accounts/{username}/reputation/` returns paginated reputation
  event history.
- [x] `GET /accounts/{username}/profile/` returns `display_name`,
  `reputation_score`, `badge_count`.
- [x] Both endpoints return 404 for nonexistent users.
- [x] Both endpoints are publicly readable.
- [x] `reputation_score` returns the raw field value (no aggregation).

Verification:

- [x] Tests pass: `pytest apps/api/tests/accounts/test_reputation.py -v`

Files likely touched:

- `apps/api/accounts/views.py` (add reputation/profile views)
- `apps/api/accounts/account_urls.py` (add reputation/profile routes)
- `apps/api/tests/accounts/test_reputation.py` (new)

Dependencies: Task 3.

Estimated scope: Small.

### Checkpoint: Auxiliary Endpoints

- [x] Bookmarks, follows, badges, and reputation endpoints work end-to-end.
- [x] Self-follow is rejected.
- [x] Permission checks pass: auth-required for mutations, public for reads.
- [x] Pagination works on all list endpoints.

### Phase 5: Duplicate Reports and Admin (completed)

#### Task 14: Duplicate report endpoints

Implement `POST /recommendations/{id}/report-duplicate/` (authenticated) and
`GET /recommendations/{id}/duplicate-reports/` (admin only).

Acceptance criteria:

- [x] `POST /recommendations/{id}/report-duplicate/` creates a
  `DuplicateReport` with status PENDING.
- [x] Request body accepts optional `suspected_duplicate_of` (integer
  recommendation id) and
  optional `reason` (string).
- [x] Returns 409 if user has already filed a report for this recommendation.
- [x] Returns 400 if `suspected_duplicate_of` references the same
  recommendation (self-reference).
- [x] `GET /recommendations/{id}/duplicate-reports/` returns paginated list.
- [x] `GET /recommendations/{id}/duplicate-reports/` returns 403 for
  non-admin users.
- [x] Each view has `@extend_schema` documentation.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_duplicate_reports.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `DuplicateReportView`,
  `DuplicateReportListView`)
- `apps/api/tests/recommendations/test_duplicate_reports.py` (new)

Dependencies: Task 5.

Estimated scope: Medium.

#### Task 15: Stake add and reclaim endpoints

Implement `POST /recommendations/{id}/stake/` (add stake),
`DELETE /recommendations/{id}/stake/` (reclaim), and
`GET /recommendations/{id}/stake/history/` (participant history).

Acceptance criteria:

- [x] `POST /recommendations/{id}/stake/` is top-up only: requires an existing
  `RecommenderParticipant` for the caller (400 if none) and never changes
  `is_active`, `BookRecommendation.status`, `current_recommender`, or
  `recommendation_cycle_number`.
- [x] Validates minimum top-up: 50,000,000 lamports above the existing
  qualifying balance (activation minimums are enforced by recommend/reactivate).
- [x] Rejects withdrawal that would leave balance between 1 and 199,999,999.
- [x] `DELETE /recommendations/{id}/stake/` sets `locked_amount_lamports` to 0,
  sets `reclaimed_at`, sets `is_active` to False.
- [x] `DELETE /recommendations/{id}/stake/` clears `current_recommender` when
  the reclaimed participant was the current recommender (decision 0011: the
  field is null when the account is no longer staked on an active cycle).
- [x] `DELETE /recommendations/{id}/stake/` returns 400 if no active stake.
- [x] `GET /recommendations/{id}/stake/history/` returns paginated
  `RecommenderParticipant` history ordered by `reactivation_number`.
- [x] Both mutating endpoints return `solana_hints` in the response.
- [x] Uses `select_for_update()` on parent `BookRecommendation`.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_stake.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `StakeView`, `StakeHistoryView`)
- `apps/api/tests/recommendations/test_stake.py` (new)

Dependencies: Task 6.

Estimated scope: Large.

#### Task 16: Comprehensive throttle test coverage

Verify that all mutating endpoints enforce rate limits correctly. Test that
throttle classes are applied to every mutating view and that the rates match
the specification.

Acceptance criteria:

- [x] Every mutating endpoint has throttle classes applied.
- [x] Tests verify 429 response when rate limit is exceeded.
- [x] Read-only endpoints use the public read throttle (60/min).
- [x] Throttle rates match the rate limiting table in this plan.

Verification:

- [x] Tests pass: `pytest apps/api/tests/recommendations/test_throttles.py -v`

Files likely touched:

- `apps/api/tests/recommendations/test_throttles.py` (new)

Dependencies: Tasks 4-15.

Estimated scope: Medium.

### Checkpoint: Complete

- [x] All 25 endpoints implement the behaviors defined in the endpoint catalog.
- [x] All mutating endpoints have throttle classes applied.
- [x] Permission checks match the permissions matrix.
- [x] Solana transaction hints are included in all stake/recommend/reactivate
  mutating responses (report-duplicate is a DB-only mutation and correctly
  returns none).
- [x] `manage.py test` passes for all recommendation endpoint tests.
- [x] OpenAPI schema generates correctly for all new endpoints.
- [x] No regressions in existing auth endpoint tests.

### Phase 6: Cover Art and Profile Images (reserve fields)

Add optional, nullable image URL fields to recommendations (cover art) and user
profiles (profile picture) so the schema is ready for imagery. This phase only
adds the fields and exposes them on read/write endpoints — no upload plumbing.

The upload feature is deferred until after MVP (see Open Question 5). Until
then, the fields are plain URL strings with no storage-URL validation and no
requirement that values be Beacon-hosted; that validation lands together with
the upload feature so existing values are not wrongly rejected.

#### Task 17: Recommendation cover image

Add an optional `cover_image_url` field to `BookRecommendation` and expose it
through the recommendation serializers.

Acceptance criteria:

- [ ] `BookRecommendation.cover_image_url` is a nullable, blank-by-default
  `URLField` with `max_length=2048` (object-store public URLs outgrow the
  default 200-char limit).
- [ ] Migration generated by `makemigrations`.
- [ ] `RecommendationSummarySerializer` and `RecommendationDetailSerializer`
  include `cover_image_url` (null when not set).
- [ ] `RecommendationCreateSerializer` and `UpdateRecommendationSerializer`
  accept an optional `cover_image_url` and store it.
- [ ] `GET /api/recommendations/` list response includes `cover_image_url`
  (null when not set).

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_cover_image.py -v`
- [ ] `uv run python manage.py makemigrations --check --dry-run` shows no
  pending changes.

Files likely touched:

- `apps/api/recommendations/models.py` (add field)
- `apps/api/recommendations/migrations/` (new migration)
- `apps/api/recommendations/serializers.py` (summary, detail, create, update)
- `apps/api/tests/recommendations/test_cover_image.py` (new)

Dependencies: Task 5.

Estimated scope: Small.

#### Task 18: User profile picture

Add an optional `avatar_url` field to the user account model and expose it in
profile serializers.

Acceptance criteria:

- [ ] `Account.avatar_url` is a nullable, blank-by-default `URLField` with
  `max_length=2048` (same reason as Task 17).
- [ ] Migration generated by `makemigrations`.
- [ ] `ProfileSerializer` includes `avatar_url` (null when not set).
- [ ] `AccountRefSerializer` includes `avatar_url` so nested creator/current
  recommender/follower/followee/badge responses carry it.
- [ ] `GET /api/accounts/{username}/profile/` returns `avatar_url`.
- [ ] No self-update endpoint in this task; a profile edit path ships with
  the upload feature (see Open Question 5).

Verification:

- [ ] Tests pass: `pytest apps/api/tests/accounts/test_avatar.py -v`
- [ ] `uv run python manage.py makemigrations --check --dry-run` shows no
  pending changes.

Files likely touched:

- `apps/api/accounts/models.py` (add field)
- `apps/api/accounts/migrations/` (new migration)
- `apps/api/recommendations/serializers.py` (`AccountRefSerializer`,
  `ProfileSerializer`)
- `apps/api/tests/accounts/test_avatar.py` (new)

Dependencies: Task 5, Task 13.

Estimated scope: Small.

### Checkpoint: Media Fields

- [ ] Cover art and profile picture fields exist, are nullable/optional, and
  are exposed on all relevant read and write endpoints.
- [ ] No file upload infrastructure was added.
- [ ] Existing tests still pass unchanged.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Concurrent supporter_number race condition | High | Use `select_for_update()` on `BookRecommendation` before computing next `supporter_number`. |
| Concurrent is_active toggles for recommender participants | Medium | Use `select_for_update()` on parent `BookRecommendation` row. |
| On-chain state drift from backend cache | Medium | Backend stores on-chain references as cache only; source of truth remains Solana programs. |
| Premature reward formula implementation | High | Store raw amounts only; aggregation formula is an open question. |
| Support-during-INACTIVE state transition complexity | Medium | Implement inside `transaction.atomic()` with clear branching logic. Test both paths (with and without active recommender). |
| Large plan scope (25 endpoints) | Medium | Vertical slicing: each phase delivers testable, working functionality. Checkpoints after every 2-3 tasks. |
| Enumerable integer resource ids in URLs | Low | Accepted leak. Ids are BigAutoField sequence values; they reveal total insert attempts and creation order, but the current row count is already public via list `count` and the public-read endpoints. Not a security boundary — authorization (creator-only updates, authenticated reads) is enforced per endpoint. Do not treat id secrecy as a control. Revisit only if per-user private data is ever keyed to recommendation ids. |

## Open Questions

**Question 1:** Should duplicate report status transitions
(PENDING -> CONFIRMED_DUPLICATE / NOT_DUPLICATE) be exposed as explicit API
actions or handled through admin?

*Answer:* Admin-only via Django admin for MVP. Community moderation is future work.

*When to revisit:* When duplicate report volume exceeds what one admin can handle,
or when a community review panel is established. At that point, add
`POST /duplicate-reports/{id}/resolve/` with a new permission class
(e.g., `IsReviewPanelMember`).

**Question 2:** Should the backend provide Solana transaction construction hints
inline in the recommend/reactivate/support responses, or through separate
`/transaction-construction` endpoints?

*Answer:* Inline in responses. SDK extracts from payload.

*Why inline is correct for MVP:*

1. The hints are mostly static (program ID, PDA seeds, amounts). The SDK
   fetches fresh blockhash from RPC at signing time, not from the backend.
2. Round-trip reduction matters for UX: backend validates and creates record,
   response includes hints, SDK builds and signs transaction.
3. Complexity budget: separate endpoints mean new URL patterns, serializers,
   permissions, rate limits, and tests for flows that fit cleanly inline.

*When to revisit:* If Beacon adds multi-instruction transactions (e.g.,
stake + vote + badge mint in one transaction) or complex CPI calls that
require separate account resolution.

**Question 3:** What is the exact reputation aggregation formula?

*Deferred.* The API returns raw event history and `Account.reputation_score`.
A future aggregation process will compute the score. This plan does not
implement the formula.

**Question 4:** Should pagination use cursor-based or page-number?

*Answer:* Page-number for MVP (default 20, max 100).

*When to revisit:* If OFFSET performance matters at scale, add `?cursor=`
as an alternative parameter. Both can coexist.

**Question 5:** Where should cover art and profile images be hosted, and who
sets them?

*Answer (partial):* The schema fields are added now as reserve
(`BookRecommendation.cover_image_url`, `Account.avatar_url`), optional and
nullable, with no upload infrastructure. The upload feature is deferred until
after MVP: presigned PUT to an S3-compatible object store (works on the
current Vercel Hobby + Neon free tier because file bytes never pass through
the API or Postgres — serverless filesystem is ephemeral and Postgres is not
blob storage).

*Still open (post-MVP, with the upload feature):* Concrete provider and
limits. Recommended: Cloudflare R2 (S3-compatible, 10 GB free, no egress
fees, portable — consistent with the no-provider-lock-in decision in plan
0015). Alternative: Vercel Blob (500 MB free, ~4.5 MB max upload on Hobby;
Vercel-specific but zero extra provider setup). Proposed limits: 5 MB max,
jpg/png/webp only. Until uploads ship, the URL fields are unvalidated strings;
storage-URL validation lands with the upload feature.
