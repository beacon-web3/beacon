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

- 28 API endpoints across 7 resource groups (Recommendations, Stake, Bookmarks,
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

- All endpoints live under `/api/v1/`.
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
| `GET` | `/api/v1/recommendations/` | List canonical recommendations with filtering and pagination. | Optional | Yes |
| `POST` | `/api/v1/recommendations/` | Create a new book recommendation (candidate or canonical). | Required | Yes (client-generated idempotency key) |
| `GET` | `/api/v1/recommendations/{id}/` | Retrieve a single recommendation. | Optional | Yes |
| `PATCH` | `/api/v1/recommendations/{id}/` | Update recommendation metadata (creator only, before activation). | Required | No |
| `POST` | `/api/v1/recommendations/{id}/recommend/` | Activate (recommend) an inactive recommendation with recommender stake. | Required | Yes |
| `POST` | `/api/v1/recommendations/{id}/reactivate/` | Reactivate an inactive recommendation with recommender stake. | Required | Yes |
| `POST` | `/api/v1/recommendations/{id}/support/` | Support a recommendation with fixed 0.01 SOL contribution. | Required | Yes |
| `GET` | `/api/v1/recommendations/{id}/supports/` | List supports for a recommendation. | Optional | Yes |

#### Filtering and Pagination

`GET /api/v1/recommendations/` supports:

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
| `POST` | `/api/v1/recommendations/{id}/stake/` | Add locked SOL to an existing recommender position. | Required | Yes |
| `DELETE` | `/api/v1/recommendations/{id}/stake/` | Reclaim all locked SOL from an active recommender position. | Required | No |
| `GET` | `/api/v1/recommendations/{id}/stake/history/` | List recommender participant history for a recommendation. | Optional | Yes |

#### Stake Validation Rules

- Minimum activation/reactivation stake: 200,000,000 lamports (0.2 SOL).
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
| `POST` | `/api/v1/recommendations/{id}/bookmark/` | Bookmark a recommendation. | Required | Yes |
| `DELETE` | `/api/v1/recommendations/{id}/bookmark/` | Remove bookmark. | Required | No |
| `GET` | `/api/v1/accounts/me/bookmarks/` | List current user's bookmarked recommendations. | Required | Yes |

### Curator Follows

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/v1/accounts/{username}/follow/` | Follow a curator. | Required | Yes |
| `DELETE` | `/api/v1/accounts/{username}/follow/` | Unfollow a curator. | Required | No |
| `GET` | `/api/v1/accounts/{username}/followers/` | List followers of a curator. | Optional | Yes |
| `GET` | `/api/v1/accounts/{username}/following/` | List curators a user follows. | Optional | Yes |

Self-follow is rejected at the application level (enforced by
`curatorfollow_no_self_follow` constraint).

### Badges

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `GET` | `/api/v1/recommendations/{id}/badges/` | List badges for a recommendation. | Optional | Yes |
| `GET` | `/api/v1/accounts/{username}/badges/` | List badges earned by a user. | Optional | Yes |

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
| `GET` | `/api/v1/accounts/{username}/reputation/` | Read reputation event history for a user. | Optional | Yes |
| `GET` | `/api/v1/accounts/{username}/profile/` | Read public profile summary (display name, reputation score, badge count). | Optional | Yes |

The exact reputation aggregation formula is not implemented. The API returns
the raw event history and the `Account.reputation_score` field. A future
aggregation process will compute the score.

### Duplicate Reports

| Method | Path | Description | Auth | Idempotent |
|--------|------|-------------|------|------------|
| `POST` | `/api/v1/recommendations/{id}/report-duplicate/` | File a duplicate report against a recommendation. | Required | Yes |
| `GET` | `/api/v1/recommendations/{id}/duplicate-reports/` | List duplicate reports for a recommendation (admin only). | Required (admin) | Yes |

#### Duplicate Report Request Body

```json
{
  "suspected_duplicate_of": "uuid (optional — recommendation UUID of suspected original)",
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
  confirms a transaction.
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
| `POST /api/v1/recommendations/` | RecommendationMutationRateThrottle | 10/min |
| `POST /api/v1/recommendations/{id}/recommend/` | RecommendationMutationRateThrottle | 5/min |
| `POST /api/v1/recommendations/{id}/reactivate/` | RecommendationMutationRateThrottle | 5/min |
| `POST /api/v1/recommendations/{id}/support/` | RecommendationMutationRateThrottle | 20/min |
| `POST /api/v1/recommendations/{id}/stake/` | RecommendationMutationRateThrottle | 5/min |
| `DELETE /api/v1/recommendations/{id}/stake/` | RecommendationMutationRateThrottle | 5/min |
| `POST /api/v1/recommendations/{id}/bookmark/` | RecommendationMutationRateThrottle | 10/min |
| `POST /api/v1/accounts/{username}/follow/` | RecommendationMutationRateThrottle | 10/min |
| `POST /api/v1/recommendations/{id}/report-duplicate/` | RecommendationMutationRateThrottle | 5/min |
| List endpoints | Public read | 60/min |

Throttle rates are configured in `settings.RECOMMENDATION_THROTTLE_RATES`
following the same pattern as `AUTH_THROTTLE_RATES`.

## State Transitions

### Support During INACTIVE

When a support is filed against an INACTIVE recommendation:

1. Create the `Support` record with the next `supporter_number`.
2. Increment `BookRecommendation.support_count`.
3. Set `BookRecommendation.last_support_at` to now.
4. If the recommendation has an existing `RecommenderParticipant` with
   `is_active=True`: set `BookRecommendation.status` to `ACTIVE`,
   set `activated_at` to now, clear `deactivated_at`.
5. If no active `RecommenderParticipant` exists: the recommendation stays
   INACTIVE (support is recorded but the cycle is not activated — a
   recommender must stake to activate).

All four steps run inside a single `transaction.atomic()` block with
`select_for_update()` on the `BookRecommendation` row.

## Response Formats

### Recommendation Summary (list, public)

```json
{
  "results": [
    {
      "id": "uuid",
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
    "id": "uuid",
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
      "pda_seeds": ["recommendation", "uuid"]
    }
  }
}
```

### Support Response (with Solana hints)

```json
{
  "support": {
    "id": "uuid",
    "supporter_number": 43,
    "amount_lamports": 10000000,
    "recommendation_cycle_number": 1,
    "created_at": "2026-01-20T14:30:00Z"
  },
  "solana_hints": {
    "program_id": "...",
    "support_account_pda": "...",
    "recommendation_account": "...",
    "amount_lamports": 10000000,
    "pda_seeds": ["support", "recommendation_uuid", "43"]
  }
}
```

### Recommend/Reactivate Response (with Solana hints)

```json
{
  "recommendation": { "...full detail fields..." },
  "recommender_participant": {
    "id": "uuid",
    "locked_amount_lamports": 200000000,
    "reactivation_number": 1,
    "is_active": true
  },
  "solana_hints": {
    "program_id": "...",
    "stake_account_pda": "...",
    "recommendation_account": "...",
    "amount_lamports": 200000000,
    "pda_seeds": ["stake", "recommendation_uuid", "user_wallet"]
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

### Phase 1: Foundation

#### Task 1: Recommendation serializers

Create `apps/api/recommendations/serializers.py` with all serializers needed
across the recommendation lifecycle endpoints. This includes input serializers
(plain `serializers.Serializer`), output serializers (`ModelSerializer` with
`read_only_fields`), and envelope wrappers.

Input serializers: `CreateRecommendationSerializer`,
`UpdateRecommendationSerializer`, `RecommendSerializer` (activate),
`ReactivateSerializer`, `SupportSerializer`, `StakeAddSerializer`,
`BookmarkSerializer`, `CuratorFollowSerializer`,
`DuplicateReportSerializer`.

Output serializers: `RecommendationSummarySerializer` (public list fields),
`RecommendationDetailSerializer` (full fields for authenticated users),
`RecommenderParticipantSerializer`, `SupportSerializer` (read),
`BookmarkReadSerializer`, `CuratorFollowSerializer` (read),
`BadgeSerializer`, `ReputationEventSerializer`,
`DuplicateReportSerializer` (read), `ProfileSerializer`.

Envelope wrappers: `RecommendationEnvelopeSerializer`,
`RecommendationListEnvelopeSerializer`, `SupportEnvelopeSerializer`,
`DetailEnvelopeSerializer`.

Acceptance criteria:

- [ ] Every endpoint in the catalog has a corresponding input and output serializer.
- [ ] Summary serializer excludes `current_recommender`, `on_chain_*`,
  `duplicate_risk_status`, `review_status`, `creator`.
- [ ] Detail serializer includes all model fields.
- [ ] Input serializers validate per the stake validation rules (0.2 SOL
  minimum, 0.05 SOL top-up minimum, no dust balance).
- [ ] `SupportSerializer` input has no user-provided amount (fixed at
  10,000,000 lamports).
- [ ] `DuplicateReportSerializer` input accepts optional `suspected_duplicate_of`
  (UUID) and optional `reason` (string).

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_serializers.py -v`
- [ ] `python manage.py check` passes.

Files likely touched:

- `apps/api/recommendations/serializers.py` (new)
- `apps/api/tests/recommendations/test_serializers.py` (new)

Dependencies: None.

Estimated scope: Large (5+ serializers, 200+ lines).

#### Task 2: URL routing and throttle classes

Create `apps/api/recommendations/urls.py` with all URL patterns matching the
endpoint catalog. Create `apps/api/recommendations/throttles.py` with a
`RecommendationMutationRateThrottle` class following the `AuthRateThrottle`
pattern. Register the recommendations URL conf in the root `urls.py`.

Acceptance criteria:

- [ ] All 28 endpoints from the catalog have URL patterns.
- [ ] URLs use `path()` with trailing slashes and named URLs.
- [ ] Root `urls.py` includes `path("api/", include("recommendations.urls"))`.
- [ ] `RecommendationMutationRateThrottle` subclasses `SimpleRateThrottle`,
  reads rate from `settings.RECOMMENDATION_THROTTLE_RATES`.
- [ ] All mutating views reference the throttle class.

Verification:

- [ ] `python manage.py check` passes.
- [ ] `python manage.py showmigrations recommendations` shows migration applied.
- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_urls.py -v`

Files likely touched:

- `apps/api/recommendations/urls.py` (new)
- `apps/api/recommendations/throttles.py` (new)
- `apps/api/beacon_api/urls.py` (add include)
- `apps/api/beacon_api/settings.py` (add `RECOMMENDATION_THROTTLE_RATES`)
- `apps/api/tests/recommendations/test_urls.py` (new)

Dependencies: Task 1.

Estimated scope: Medium.

#### Task 3: Recommendation model factories

Extend `apps/api/tests/recommendations/factories.py` with factories for all
9 recommendation models. Add `RecommendationFactory`, `DuplicateReportFactory`,
`RecommenderParticipantFactory`, `SupportFactory`, `BookmarkFactory`,
`CuratorFollowFactory`, `BadgeFactory`, `ReputationEventFactory`,
`CategoryFactory`.

Acceptance criteria:

- [ ] Each factory creates a valid model instance with sensible defaults.
- [ ] Factories support overrides for all critical fields (status, amounts, etc.).
- [ ] `RecommendationFactory` default status is INACTIVE.
- [ ] `SupportFactory` default `amount_lamports` is 10,000,000.
- [ ] `RecommenderParticipantFactory` default `locked_amount_lamports` is
  200,000,000.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_models.py -v`

Files likely touched:

- `apps/api/tests/recommendations/factories.py` (extend)
- `apps/api/tests/recommendations/test_models.py` (extend)

Dependencies: Task 1.

Estimated scope: Small.

### Checkpoint: Foundation

- [ ] All serializers validate correctly against model constraints.
- [ ] All URL patterns resolve.
- [ ] `python manage.py check` passes.
- [ ] `manage.py test` passes for serializer and URL tests.

### Phase 2: Recommendation CRUD

#### Task 4: Recommendation list and detail endpoints

Implement `GET /api/v1/recommendations/` (list with filtering and pagination)
and `GET /api/v1/recommendations/{id}/` (detail). List endpoint uses summary
serializer (public); detail endpoint uses detail serializer for authenticated
users and summary serializer for anonymous.

Acceptance criteria:

- [ ] `GET /recommendations/` returns paginated list with summary fields.
- [ ] All filter parameters work: `status`, `page_type`, `category`,
  `duplicate_risk_status`, `review_status`, `creator`, `is_canonical`,
  `search`, `ordering`.
- [ ] `search` requires minimum 3 characters; shorter queries return empty
  results.
- [ ] `page_size` defaults to 20, max 100.
- [ ] `GET /recommendations/{id}/` returns detail fields for authenticated
  users.
- [ ] `GET /recommendations/{id}/` returns summary fields for anonymous users.
- [ ] `GET /recommendations/{id}/` returns 404 for nonexistent IDs.
- [ ] Every view has `@extend_schema` documentation.
- [ ] Throttle class is applied to list endpoint.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_recommendation_list.py -v`
- [ ] Manual check: `curl` list and detail endpoints return expected shapes.

Files likely touched:

- `apps/api/recommendations/views.py` (new — `RecommendationListView`,
  `RecommendationDetailView`)
- `apps/api/recommendations/serializers.py` (may need adjustments)
- `apps/api/tests/recommendations/test_recommendation_list.py` (new)

Dependencies: Tasks 1, 2, 3.

Estimated scope: Large.

#### Task 5: Recommendation create and update endpoints

Implement `POST /api/v1/recommendations/` (create) and
`PATCH /api/v1/recommendations/{id}/` (update metadata). Create endpoint
requires authentication. Update is restricted to the creator and only allowed
before activation (status is INACTIVE and `recommendation_cycle_number == 0`).

Acceptance criteria:

- [ ] `POST /recommendations/` creates a recommendation with status INACTIVE.
- [ ] `POST /recommendations/` requires authentication (403 for anonymous).
- [ ] `POST /recommendations/` validates unique canonical constraint
  (title + author + page_type).
- [ ] `PATCH /recommendations/{id}/` updates metadata fields only.
- [ ] `PATCH /recommendations/{id}/` returns 403 for non-creators.
- [ ] `PATCH /recommendations/{id}/` returns 400 if recommendation is already
  active (`recommendation_cycle_number > 0`).
- [ ] `POST /recommendations/` is idempotent (client-generated idempotency key).
- [ ] Every view has `@extend_schema` documentation.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_recommendation_create.py -v`
- [ ] Manual check: create, update, and verify permissions.

Files likely touched:

- `apps/api/recommendations/views.py` (add `RecommendationCreateView`,
  `RecommendationUpdateView`)
- `apps/api/recommendations/serializers.py` (may need adjustments)
- `apps/api/tests/recommendations/test_recommendation_create.py` (new)

Dependencies: Task 4.

Estimated scope: Medium.

### Checkpoint: Recommendation CRUD

- [ ] Create, read, update, list, filter, and paginate work end-to-end.
- [ ] Permission checks pass: creator-only update, auth-only create.
- [ ] Search with < 3 characters returns empty results.
- [ ] OpenAPI schema generates correctly for recommendation endpoints.

### Phase 3: Activation and Support

#### Task 6: Recommend (activate) endpoint

Implement `POST /api/v1/recommendations/{id}/recommend/` which activates an
inactive recommendation for the first time. Creates a `RecommenderParticipant`
with `is_active=True`, sets `current_recommender`, increments
`recommendation_cycle_number`, sets `status` to ACTIVE, and records
`activated_at`. Returns Solana transaction hints inline.

Acceptance criteria:

- [ ] `POST /recommendations/{id}/recommend/` creates a `RecommenderParticipant`.
- [ ] `BookRecommendation.status` changes from INACTIVE to ACTIVE.
- [ ] `BookRecommendation.current_recommender` is set to the requesting user.
- [ ] `BookRecommendation.recommendation_cycle_number` increments.
- [ ] `BookRecommendation.activated_at` is set.
- [ ] Returns 400 if recommendation is already ACTIVE.
- [ ] Returns 400 if user already has an active participant on this recommendation.
- [ ] Uses `select_for_update()` on `BookRecommendation` for concurrency safety.
- [ ] Response includes `solana_hints` with program ID, PDA seeds, amount.
- [ ] Operation runs inside `transaction.atomic()`.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_recommend.py -v`
- [ ] Concurrency test: two simultaneous requests, only one succeeds.

Files likely touched:

- `apps/api/recommendations/views.py` (add `RecommendView`)
- `apps/api/tests/recommendations/test_recommend.py` (new)

Dependencies: Task 5.

Estimated scope: Medium.

#### Task 7: Reactivate endpoint

Implement `POST /api/v1/recommendations/{id}/reactivate/` which reactivates
an inactive recommendation that has a previous cycle. Creates a new
`RecommenderParticipant` (incrementing `reactivation_number`), updates
`current_recommender`, increments `recommendation_cycle_number`, sets
`status` to ACTIVE, clears `deactivated_at`. Returns Solana transaction hints.

Acceptance criteria:

- [ ] `POST /recommendations/{id}/reactivate/` creates a new
  `RecommenderParticipant` with incremented `reactivation_number`.
- [ ] `BookRecommendation.status` changes to ACTIVE.
- [ ] `BookRecommendation.deactivated_at` is cleared.
- [ ] Returns 400 if recommendation is already ACTIVE.
- [ ] Returns 400 if `recommendation_cycle_number == 0` (use recommend instead).
- [ ] Uses `select_for_update()` on `BookRecommendation`.
- [ ] Response includes `solana_hints`.
- [ ] Runs inside `transaction.atomic()`.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_reactivate.py -v`

Dependencies: Task 6.

Estimated scope: Medium.

#### Task 8: Support endpoint

Implement `POST /api/v1/recommendations/{id}/support/` which creates a fixed
0.01 SOL support contribution. Increments `supporter_number` atomically,
increments `support_count`, updates `last_support_at`. If the recommendation
is INACTIVE and has an active `RecommenderParticipant`, transitions to ACTIVE
(see State Transitions section). Returns Solana transaction hints.

Acceptance criteria:

- [ ] `POST /recommendations/{id}/support/` creates a `Support` record with
  `amount_lamports=10_000_000`.
- [ ] `supporter_number` is incremented atomically (no duplicates).
- [ ] `BookRecommendation.support_count` is incremented.
- [ ] `BookRecommendation.last_support_at` is updated.
- [ ] Support during INACTIVE with active recommender transitions to ACTIVE.
- [ ] Support during INACTIVE without active recommender stays INACTIVE.
- [ ] One support per supporter per recommendation (returns 409 on duplicate).
- [ ] Uses `select_for_update()` on `BookRecommendation` for supporter_number.
- [ ] Response includes `solana_hints`.
- [ ] Runs inside `transaction.atomic()`.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_support.py -v`
- [ ] Concurrency test: simultaneous supports get different `supporter_number`.

Files likely touched:

- `apps/api/recommendations/views.py` (add `SupportView`)
- `apps/api/tests/recommendations/test_support.py` (new)

Dependencies: Task 5.

Estimated scope: Large.

#### Task 9: Support list endpoint

Implement `GET /api/v1/recommendations/{id}/supports/` which lists supports
for a recommendation, ordered by `supporter_number`.

Acceptance criteria:

- [ ] Returns paginated list of supports.
- [ ] Supports are ordered by `supporter_number` ascending.
- [ ] Each support includes `supporter_number`, `amount_lamports`,
  `recommendation_cycle_number`, `created_at`.
- [ ] Supports are publicly readable.
- [ ] Returns 404 for nonexistent recommendation.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_support_list.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `SupportListView`)
- `apps/api/tests/recommendations/test_support_list.py` (new)

Dependencies: Task 8.

Estimated scope: Small.

### Checkpoint: Activation and Support

- [ ] Recommend, reactivate, and support endpoints work end-to-end.
- [ ] Support during INACTIVE correctly transitions to ACTIVE when applicable.
- [ ] `supporter_number` is unique per recommendation (no races).
- [ ] Solana hints are included in all mutating responses.
- [ ] Concurrency tests pass for supporter_number and status transitions.

### Phase 4: Auxiliary Endpoints

#### Task 10: Bookmark endpoints

Implement `POST /recommendations/{id}/bookmark/`,
`DELETE /recommendations/{id}/bookmark/`, and
`GET /accounts/me/bookmarks/`. Toggle pattern (POST to add, DELETE to remove).

Acceptance criteria:

- [ ] `POST /recommendations/{id}/bookmark/` creates a bookmark (201).
- [ ] `POST /recommendations/{id}/bookmark/` returns 409 if already bookmarked.
- [ ] `DELETE /recommendations/{id}/bookmark/` removes bookmark (204).
- [ ] `DELETE /recommendations/{id}/bookmark/` returns 404 if not bookmarked.
- [ ] `GET /accounts/me/bookmarks/` returns current user's bookmarks.
- [ ] All bookmark endpoints require authentication.
- [ ] Each view has `@extend_schema` documentation.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_bookmarks.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add `BookmarkView`,
  `UserBookmarksView`)
- `apps/api/tests/recommendations/test_bookmarks.py` (new)

Dependencies: Task 5.

Estimated scope: Medium.

#### Task 11: Curator follow endpoints

Implement `POST /accounts/{username}/follow/`,
`DELETE /accounts/{username}/follow/`,
`GET /accounts/{username}/followers/`, and
`GET /accounts/{username}/following/`. These live in the accounts app since
they're under `/accounts/`.

Acceptance criteria:

- [ ] `POST /accounts/{username}/follow/` creates a follow (201).
- [ ] `POST /accounts/{username}/follow/` returns 400 for self-follow.
- [ ] `POST /accounts/{username}/follow/` returns 409 if already following.
- [ ] `DELETE /accounts/{username}/follow/` removes follow (204).
- [ ] `GET /accounts/{username}/followers/` returns paginated follower list.
- [ ] `GET /accounts/{username}/following/` returns paginated following list.
- [ ] Follow/unfollow require authentication.
- [ ] Follower/following lists are publicly readable.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/accounts/test_follow.py -v`

Files likely touched:

- `apps/api/accounts/views.py` (add follow views)
- `apps/api/accounts/urls.py` (add follow URL patterns)
- `apps/api/tests/accounts/test_follow.py` (new)

Dependencies: Task 3.

Estimated scope: Medium.

#### Task 12: Badge endpoints

Implement `GET /recommendations/{id}/badges/` and
`GET /accounts/{username}/badges/`. Both are read-only, publicly accessible.

Acceptance criteria:

- [ ] `GET /recommendations/{id}/badges/` returns badges for a recommendation.
- [ ] `GET /accounts/{username}/badges/` returns badges earned by a user.
- [ ] Badge response includes `tier`, `earned_at`, and `recommendation` fields.
- [ ] Both endpoints are publicly readable.
- [ ] Returns empty list if no badges earned.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_badges.py -v`

Files likely touched:

- `apps/api/recommendations/views.py` (add badge views)
- `apps/api/tests/recommendations/test_badges.py` (new)

Dependencies: Task 3.

Estimated scope: Small.

#### Task 13: Reputation and profile endpoints

Implement `GET /accounts/{username}/reputation/` and
`GET /accounts/{username}/profile/`. Both are publicly readable.

Acceptance criteria:

- [ ] `GET /accounts/{username}/reputation/` returns paginated reputation
  event history.
- [ ] `GET /accounts/{username}/profile/` returns `display_name`,
  `reputation_score`, `badge_count`.
- [ ] Both endpoints return 404 for nonexistent users.
- [ ] Both endpoints are publicly readable.
- [ ] `reputation_score` returns the raw field value (no aggregation).

Verification:

- [ ] Tests pass: `pytest apps/api/tests/accounts/test_reputation.py -v`

Files likely touched:

- `apps/api/accounts/views.py` (add reputation/profile views)
- `apps/api/tests/accounts/test_reputation.py` (new)

Dependencies: Task 3.

Estimated scope: Small.

### Checkpoint: Auxiliary Endpoints

- [ ] Bookmarks, follows, badges, and reputation endpoints work end-to-end.
- [ ] Self-follow is rejected.
- [ ] Permission checks pass: auth-required for mutations, public for reads.
- [ ] Pagination works on all list endpoints.

### Phase 5: Duplicate Reports and Admin

#### Task 14: Duplicate report endpoints

Implement `POST /recommendations/{id}/report-duplicate/` (authenticated) and
`GET /recommendations/{id}/duplicate-reports/` (admin only).

Acceptance criteria:

- [ ] `POST /recommendations/{id}/report-duplicate/` creates a
  `DuplicateReport` with status PENDING.
- [ ] Request body accepts optional `suspected_duplicate_of` (UUID) and
  optional `reason` (string).
- [ ] Returns 409 if user has already filed a report for this recommendation.
- [ ] Returns 400 if `suspected_duplicate_of` references the same
  recommendation (self-reference).
- [ ] `GET /recommendations/{id}/duplicate-reports/` returns paginated list.
- [ ] `GET /recommendations/{id}/duplicate-reports/` returns 403 for
  non-admin users.
- [ ] Each view has `@extend_schema` documentation.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_duplicate_reports.py -v`

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

- [ ] `POST /recommendations/{id}/stake/` creates or updates a
  `RecommenderParticipant` with the locked amount.
- [ ] Validates minimum stake: 200,000,000 lamports for activation,
  50,000,000 lamports for top-up above qualifying balance.
- [ ] Rejects withdrawal that would leave balance between 1 and 199,999,999.
- [ ] `DELETE /recommendations/{id}/stake/` sets `locked_amount_lamports` to 0,
  sets `reclaimed_at`, sets `is_active` to False.
- [ ] `DELETE /recommendations/{id}/stake/` returns 400 if no active stake.
- [ ] `GET /recommendations/{id}/stake/history/` returns paginated
  `RecommenderParticipant` history ordered by `reactivation_number`.
- [ ] Both mutating endpoints return `solana_hints` in the response.
- [ ] Uses `select_for_update()` on parent `BookRecommendation`.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_stake.py -v`

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

- [ ] Every mutating endpoint has throttle classes applied.
- [ ] Tests verify 429 response when rate limit is exceeded.
- [ ] Read-only endpoints use the public read throttle (60/min).
- [ ] Throttle rates match the rate limiting table in this plan.

Verification:

- [ ] Tests pass: `pytest apps/api/tests/recommendations/test_throttles.py -v`

Files likely touched:

- `apps/api/tests/recommendations/test_throttles.py` (new)

Dependencies: Tasks 4-15.

Estimated scope: Medium.

### Checkpoint: Complete

- [ ] All 28 endpoints implement the behaviors defined in the endpoint catalog.
- [ ] All mutating endpoints have throttle classes applied.
- [ ] Permission checks match the permissions matrix.
- [ ] Solana transaction hints are included in all mutating responses.
- [ ] `manage.py test` passes for all recommendation endpoint tests.
- [ ] OpenAPI schema generates correctly for all new endpoints.
- [ ] No regressions in existing auth endpoint tests.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Concurrent supporter_number race condition | High | Use `select_for_update()` on `BookRecommendation` before computing next `supporter_number`. |
| Concurrent is_active toggles for recommender participants | Medium | Use `select_for_update()` on parent `BookRecommendation` row. |
| On-chain state drift from backend cache | Medium | Backend stores on-chain references as cache only; source of truth remains Solana programs. |
| Premature reward formula implementation | High | Store raw amounts only; aggregation formula is an open question. |
| Support-during-INACTIVE state transition complexity | Medium | Implement inside `transaction.atomic()` with clear branching logic. Test both paths (with and without active recommender). |
| Large plan scope (28 endpoints) | Medium | Vertical slicing: each phase delivers testable, working functionality. Checkpoints after every 2-3 tasks. |

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
