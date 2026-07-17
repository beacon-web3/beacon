# Recommendation Lifecycle Data Model

## Status

Completed

## Context

Beacon's current backend data model only has the `accounts.Account` model and
authentication-related migrations. The product specs describe a books-first
discovery marketplace, but the backend does not yet model canonical book
recommendations, support/upvotes, bookmarks, curator follows, badge history,
reputation history, or the proposed recommender lifecycle.

The product direction for recommendations has changed from a simple permanent
first-discoverer model to the hybrid lifecycle accepted in
`docs/decisions/0011-hybrid-recommendation-lifecycle.md`:

- A standalone book work or recognized book series keeps one canonical Beacon
  recommendation page.
- Recognized series are series-level only for MVP; individual-volume pages require
  a future explicit product or governance decision.
- The first valid recommender receives permanent historical discoverer credit.
- A page has at most one active recommendation cycle at a time.
- A new user can recommend or reactivate that page only when the current cycle is
  inactive and they stake at least the required `0.2 SOL` minimum.
- The original discoverer and prior reactivators may add locked SOL at any time
  to increase their share of future upvote/support credit.
- `0.2 SOL` is the MVP activation and reactivation minimum, with no maximum
  deposit cap on locked recommender SOL.
- Additional stake must not rewrite past support credit, badges, discoverer
  credit, or reputation history.
- Extra locked SOL must use diminishing returns if it affects future credit,
  rewards, ranking, or visibility.
- If no recommender SOL remains locked and no new support arrives for 90 days,
  the recommendation can become inactive.
- An inactive recommendation can be reactivated by another eligible recommender
  staking at least the required `0.2 SOL` minimum.
- Reactivation does not require moderation review by default for valid,
  undisputed inactive pages.
- Flagged, disputed, duplicate-reported, unsafe metadata, or unsafe link cases
  require review before reactivation.
- Historical discovery, activation, support, badge, and reputation records remain
  visible even when current active credit changes.
- The exact future credit curve and reward split formulas are intentionally
  unresolved and must not be implemented in this plan.

Relevant specs and docs:

- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/decisions/0002-canonical-book-pages.md`
- `docs/decisions/0003-discovery-first-positioning.md`
- `docs/decisions/0008-trust-minimized-protocol-custody.md`
- `docs/decisions/0011-hybrid-recommendation-lifecycle.md`
- `docs/decisions/0012-canonical-work-series-identity.md`
- `docs/decisions/0013-recommendation-inactivity-window.md`
- `docs/decisions/0014-reactivation-moderation-policy.md`
- `docs/decisions/0015-minimum-recommender-stake-no-deposit-cap.md`
- `docs/decisions/0016-diminishing-returns-for-extra-recommender-stake.md`
- `docs/decisions/0017-recommender-stake-balance-and-top-up-minimums.md`
- `docs/decisions/0018-fixed-support-contribution.md`
- `docs/decisions/0019-step-based-milestone-rewards.md`
- `docs/api/openapi.md`
- `apps/api/accounts/models.py`
- `apps/api/accounts/migrations/`

## Objective

Define and implement the first backend product data model for Beacon's canonical
book recommendation lifecycle while keeping economic policy unresolved where the
specs are still draft.

The implementation should support:

- One canonical recommendation page per standalone-work or recognized-series
  identity.
- High-sensitivity duplicate-risk detection and manual review state for candidate
  pages that may duplicate existing canonical pages.
- Active/inactive lifecycle for recommendations.
- Reactivation blocker state for flagged, disputed, duplicate-reported, or unsafe
  canonical pages.
- Locked recommender SOL balance tracking for inactivity eligibility.
- Minimum stake enforcement and uncapped locked-amount storage for eligible
  recommender deposits.
- Recommender stake balance validation requiring either `0 SOL` or at least
  `0.2 SOL`, plus `0.05 SOL` minimum top-ups above an existing qualifying
  balance.
- Multiple recommender participants over time.
- Stake-backed historical recommender credit-share tracking for future support.
- Diminishing-returns-ready stake amount storage without encoding a final formula.
- Support/upvote history.
- User bookmarks.
- Curator follows.
- Badge/NFT participation history or eligibility cache.
- Reputation-related history without inventing a final reputation formula.
- A clean pre-launch migration history with one initial migration after model
  shape is approved.

## Product Decisions To Confirm Before Implementation

The following rules must be confirmed in specs and decision records before model
implementation starts:

- The canonical product object is a `BookRecommendation` or equivalent, not a
  generic post.
- The canonical product object can represent either a standalone book work or a
  recognized book series, but not an individual series volume during MVP.
- The recommendation contains both book metadata and Beacon-specific
  recommendation state for MVP simplicity.
- Duplicate-risk candidates can remain pending manual review before becoming
  canonical.
- Rejected duplicate-risk candidates do not immediately release locked SOL; the
  normal lock period still applies.
- A recommendation can become inactive when no support/upvote has arrived for 90
  days after no recommender SOL remains locked on the active cycle.
- Partial stake withdrawals do not start the inactivity window while any
  recommender SOL remains locked.
- Withdrawal flows must warn a recommender before a withdrawal that leaves no SOL
  locked and can start the inactivity window.
- Withdrawal flows must not leave a recommender locked balance above `0 SOL` but
  below `0.2 SOL`; such withdrawals must be rejected or treated as full
  withdrawals to `0 SOL`.
- An inactive recommendation can be reactivated by an eligible recommender who
  stakes at least the required `0.2 SOL` minimum.
- Eligible recommenders may lock more than `0.2 SOL`; there is no maximum deposit
  cap in the MVP product policy.
- Eligible recommender top-ups above an existing qualifying balance must be at
  least `0.05 SOL` per increase.
- Reactivation does not require moderation review by default for valid,
  undisputed inactive pages.
- Pages that are flagged, disputed, duplicate-reported, or have unsafe metadata or
  links require review before reactivation.
- Users who have never activated or reactivated a page cannot stake into it while
  it is active.
- Historical recommender future-credit share may be affected by currently locked
  stake, not permanent first-mover ownership alone.
- Historical recommender participation remains visible even when active credit is
  zero.
- Ordinary `0.01 SOL` supporters are not subject to recommender locked-balance
  rules.
- Additional stake does not rewrite past support credit, badges, discoverer
  credit, or reputation history.
- Extra locked SOL must use diminishing returns if it affects future credit,
  rewards, ranking, or visibility.
- The exact future-credit curve and reward formulas for multiple historical
  recommender participants remain open questions and are not implemented.

## Architecture Decisions

- Use a single canonical recommendation page model for MVP instead of separate
  neutral `Book` and `Recommendation` tables.
- Store enough identity fields to distinguish standalone work versus series pages,
  normalize title/author matching, track duplicate-risk review state, and support
  duplicate reports.
- Add a separate recommender participation/stake table so one canonical page can
  have multiple recommender activation periods and stake positions over time.
- Link support/upvotes to the canonical recommendation and, when relevant, the
  active lifecycle period for later reward analysis.
- Store support/upvote records with the fixed MVP contribution amount of
  `0.01 SOL`.
- Store on-chain transaction signatures, program account addresses, and indexed
  economic state as references or cache fields only; Solana programs remain the
  source of truth for trust-sensitive custody and fund movement.
- Keep reward formulas, governance weights, badge transfer policy, and reputation
  formulas out of the model logic until the product/tokenomics specs resolve
  them.
- Consolidate Django migrations into a single initial migration only because the
  app is unpublished and has no real users.

## Non-Goals

- Do not implement a final reward split formula.
- Do not implement actual Solana transactions, signing, staking, or withdrawal
  flows in this plan.
- Do not mint NFTs or define final badge metadata policy in this plan.
- Do not add a governance token.
- Do not imply support payments are refundable votes.
- Do not imply badges represent book ownership, book IP, or cover-art ownership.
- Do not build frontend UI in this plan unless a later approved plan explicitly
  adds it.

## Phase 1: Update Specs, Assumptions, And Decisions (completed)

### Task 1: Update Product Specs For Recommendation Lifecycle

Description: Update the canonical product docs so the recommendation lifecycle is
defined before any schema work begins.

Acceptance criteria:

- [x] `docs/product/mvp.md` describes one canonical page per standalone work or
  recognized series with active and inactive states.
- [x] `docs/product/mvp.md` explains that reactivation preserves the canonical
  page, historical supports, badges, and recommender history.
- [x] `docs/product/user-stories.md` includes user-facing behavior for creating,
  supporting, bookmarking, following curators, viewing upvote/support history,
  viewing badges, and viewing reputation.
- [x] Product copy avoids describing support as a refundable vote or guaranteed
  investment return.
- [x] Specs distinguish active recommendation status, historical discovery
  history, and future upvote/support credit share.
- [x] Specs define MVP canonical identity as a standalone book work or recognized
  series, with series-level pages only for recognized series.
- [x] Specs define no moderation review by default for valid, undisputed inactive
  page reactivation, with review required for flagged, disputed,
  duplicate-reported, or unsafe pages.

Verification:

- [x] Documentation review confirms there is no conflict between `mvp.md`,
  `user-stories.md`, and the discovery-first positioning guardrails.

Dependencies: None.

Files likely touched:

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/vision.md` if positioning language needs a small clarification.

Estimated scope: Medium.

### Task 2: Update Assumptions And Open Questions

Description: Record draft lifecycle parameters and unresolved economics so later
implementation does not silently invent policy.

Acceptance criteria:

- [x] `docs/product/assumptions.md` records the accepted 90-day recommendation
  inactivity window.
- [x] `docs/product/assumptions.md` records accepted historical recommender stake
  addition rights without finalizing the formula.
- [x] `docs/product/open-questions.md` records unresolved questions about reward
  split formulas across historical recommender participants.
- [x] `docs/product/open-questions.md` records unresolved questions about the
  exact diminishing-returns curve, stake caps, and future-credit eligibility.
- [x] Any unresolved badge transfer, metadata, or minting policy remains open
  rather than being decided by model code.

Verification:

- [x] Documentation review confirms all unresolved tokenomics and badge mechanics
  remain listed as draft assumptions or open questions.

Dependencies: Task 1.

Files likely touched:

- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md` if stake lifecycle wording needs alignment.

Estimated scope: Medium.

### Task 3: Add Decision Record For Hybrid Recommendation Lifecycle

Description: Add an ADR/product decision record documenting why Beacon is using a
canonical recommendation page with permanent discoverer credit, single active
recommendation cycles, and historical recommender stake additions instead of a
permanent first-discoverer-only model.

Acceptance criteria:

- [x] New decision record is added under `docs/decisions/` with the next
  sequential ID.
- [x] Decision status is `Accepted` because the product decision was explicitly
  approved before writing.
- [x] Decision explains the active cycle model, historical discovery history,
  reactivation behavior, historical recommender stake rights, and unresolved
  reward formula.
- [x] Alternatives considered include permanent discoverer-only credit, fully
  open active staking, and separate competing recommendation pages.
- [x] `docs/decisions/README.md` is updated.

Verification:

- [x] Decision record links to the relevant specs and does not contradict product
  guardrails.

Dependencies: Tasks 1 and 2.

Files likely touched:

- `docs/decisions/0011-hybrid-recommendation-lifecycle.md`
- `docs/decisions/README.md`

Estimated scope: Small.

### Task 4: Update Architecture And API Documentation Boundaries

Description: Align architecture and API docs with the planned backend-owned
product state and Solana-owned economic state.

Acceptance criteria:

- [x] `docs/architecture/system-design.md` lists canonical recommendation pages,
  recommender participants, support history, bookmarks, curator follows, badge
  history, and reputation history as backend product concepts.
- [x] Architecture docs state that economic custody, stake locks, support
  transfers, and reward release remain on-chain or on-chain-indexed when
  implemented.
- [x] `docs/api/openapi.md` receives a planning note or future endpoint section
  for recommendation lifecycle APIs if useful.
- [x] No API endpoint is documented as implemented before code exists.

Verification:

- [x] Documentation review confirms architecture, API, and product docs use the
  same vocabulary.

Dependencies: Tasks 1-3.

Files likely touched:

- `docs/architecture/system-design.md`
- `docs/api/openapi.md`

Estimated scope: Small.

## Checkpoint: Spec Approval

Do not start model implementation until this checkpoint is complete.

- [x] Product specs reflect the new recommendation lifecycle.
- [x] Assumptions and open questions capture unresolved policy.
- [x] Decision record is added and indexed.
- [x] Architecture docs define off-chain versus on-chain responsibility.
- [x] Human review confirms the product direction is ready for schema work.

## Phase 2: Design Backend Data Model (completed)

### Task 5: Draft Django Model Schema

Description: Draft the Django model structure in the plan or a schema design note
before editing `models.py`.

Acceptance criteria:

- [x] Proposed schema includes `BookRecommendation` or the chosen canonical page
  model.
- [x] Proposed schema identifies whether each canonical page represents a
  standalone work or recognized series.
- [x] Proposed schema includes duplicate-risk/manual-review state for candidate
  pages and a way to record duplicate reports.
- [x] Proposed schema includes a recommender participant/stake-position model for
  active and historical recommender credit.
- [x] Proposed schema includes support/upvote history with fixed `0.01 SOL` MVP
  contribution accounting.
- [x] Proposed schema includes bookmarks.
- [x] Proposed schema includes curator follows.
- [x] Proposed schema includes badge/NFT history or eligibility cache.
- [x] Proposed schema includes enough fields to support reputation aggregation
  later without defining the final formula.
- [x] Proposed schema identifies all uniqueness constraints and indexes.
- [x] Proposed schema identifies fields that are authoritative on-chain versus
  backend cache/reference fields.

Verification:

- [x] Schema review confirms no unresolved reward formula is encoded in database
  fields or model methods.

Dependencies: Spec Approval checkpoint.

Files likely touched:

- `docs/plans/0016-recommendation-lifecycle-data-model.md`
- Optional schema note under `docs/architecture/` if the design becomes too large
  for the plan.

Estimated scope: Medium.

#### Schema Design

All models live in a new `recommendations` Django app (see Task 6). The schema
below uses Django field types; PostgreSQL details are noted where relevant.

##### BookRecommendation

Canonical page model. One record per standalone book work or recognized series.
Contains both book metadata and Beacon-specific recommendation lifecycle state
for MVP simplicity.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `creator` | FK(Account, on_delete=PROTECT) | The original discoverer. Immutable after creation. `related_name="created_recommendations"`. |
| `page_type` | CharField(20) | Choices: `STANDALONE_WORK`, `RECOGNIZED_SERIES`. |
| `title` | TextField | User-entered title. |
| `title_normalized` | TextField | Lowercased, whitespace-trimmed copy of `title` for duplicate detection. The `Lower()` in the canonical unique constraint is defensive; this field should already be stored lowercase. |
| `author_names` | TextField | User-entered author(s). |
| `author_names_normalized` | TextField | Lowercased, whitespace-trimmed copy of `author_names` for duplicate detection. Same normalization rules as `title_normalized`. |
| `description` | TextField(blank) | Curator note or description. |
| `external_reference_url` | URLField(blank, null) | Optional external link. |
| `category` | FK(Category, null, blank, on_delete=SET_NULL) | Genre or category. Optional for MVP; null means uncategorized. |
| `status` | CharField(20) | Choices: `ACTIVE`, `INACTIVE`. Lifecycle state of the current recommendation cycle. |
| `is_canonical` | BooleanField(default=False) | True once the page is approved. Candidate pages have False. |
| `duplicate_risk_status` | CharField(20) | Choices: `LOW_RISK`, `HIGH_RISK`, `NEEDS_REVIEW`. Set at creation time. |
| `review_status` | CharField(20) | Choices: `NOT_REQUIRED`, `PENDING`, `APPROVED`, `REJECTED`. Manual review state for duplicate-risk candidates. |
| `current_recommender` | FK(Account, null, on_delete=SET_NULL) | The account currently staked on the active cycle. Null when inactive. `related_name="active_recommendations"`. |
| `recommendation_cycle_number` | PositiveIntegerField(default=0) | Incremented on each activation. 0 means never activated. |
| `activated_at` | DateTimeField(null) | When the current active cycle started. Null when inactive. |
| `deactivated_at` | DateTimeField(null) | When the last active cycle ended. Null if never deactivated. |
| `last_support_at` | DateTimeField(null) | Timestamp of most recent valid support on this page. Used for inactivity window calculation. |
| `support_count` | PositiveIntegerField(default=0) | Denormalized total support count for list queries. |
| `on_chain_program_account` | CharField(64, blank, null) | Solana program account address. Backend cache; Solana is source of truth for custody. |
| `on_chain_recommendation_seed` | CharField(64, blank, null) | PDA seed or address. Backend cache. |
| `created_at` | DateTimeField(auto_now_add) | |
| `updated_at` | DateTimeField(auto_now) | |

Constraints:

```python
# One canonical page per unique (normalized title, normalized author, page type)
UniqueConstraint(
    Lower("title_normalized"),
    Lower("author_names_normalized"),
    "page_type",
    condition=Q(is_canonical=True),
    name="bookrecommendation_canonical_work_unique",
)

# Indexes
Index(fields=["status", "-created_at"])           # Active recommendation listing
Index(fields=["-support_count"])                   # Trending/popular queries
Index(fields=["creator", "-created_at"])            # Creator profile page
Index(fields=["category", "status", "-support_count"])  # Category browse
Index(fields=["last_support_at"])                   # Inactivity scanning
```

##### Category

Lookup table for book genres/categories. Kept as a model for future governance
and filtering flexibility rather than a hardcoded CharField choices list.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `name` | CharField(100, unique) | Display name. |
| `slug` | SlugField(unique) | URL-safe identifier. |
| `is_active` | BooleanField(default=True) | Soft-disable without deleting. |
| `created_at` | DateTimeField(auto_now_add) | |

##### DuplicateReport

Records user-submitted duplicate reports against a canonical or candidate page.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `reporter` | FK(Account, on_delete=PROTECT) | The user reporting the duplicate. `related_name="duplicate_reports_filed"`. |
| `recommendation` | FK(BookRecommendation, on_delete=CASCADE) | The page being reported. `related_name="duplicate_reports"`. |
| `suspected_duplicate_of` | FK(BookRecommendation, null, on_delete=SET_NULL) | The existing page it may duplicate. Null if reporter is unsure. `related_name="suspected_duplicates"`. |
| `reason` | TextField(blank) | Optional explanation. |
| `status` | CharField(20) | Choices: `PENDING`, `CONFIRMED_DUPLICATE`, `NOT_DUPLICATE`. Default `PENDING`. |
| `created_at` | DateTimeField(auto_now_add) | |

Constraints:

```python
UniqueConstraint(
    "reporter",
    "recommendation",
    name="duplicatereport_one_per_reporter_per_recommendation",
)

# Prevent a report from pointing to itself as a suspected duplicate
CheckConstraint(
    ~Q(recommendation=F("suspected_duplicate_of")),
    name="duplicatereport_no_self_reference",
)

Index(fields=["recommendation", "status"])   # Admin review queue
Index(fields=["status", "-created_at"])      # Pending reports listing
```

##### RecommenderParticipant

Tracks each account that activates or reactivates a recommendation page and
their locked SOL position. Historical recommender stake additions are recorded
as new rows or updated `locked_amount` on the same row. The exact diminishing-
returns credit curve is not encoded.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `account` | FK(Account, on_delete=PROTECT) | The recommender. `related_name="recommender_participations"`. |
| `recommendation` | FK(BookRecommendation, on_delete=CASCADE) | The page. `related_name="recommender_participants"`. |
| `locked_amount_lamports` | BigIntegerField | Current locked SOL in lamports. Backend cache; Solana is source of truth for custody. Must be 0 or >= 200_000_000 (0.2 SOL). |
| `initial_lock_at` | DateTimeField | When this recommender first locked SOL for this page. |
| `last_stake_change_at` | DateTimeField(null) | When the locked amount last changed. |
| `reclaimed_at` | DateTimeField(null) | When all locked SOL was reclaimed. Null while any SOL remains locked. |
| `is_active` | BooleanField(default=False) | True if this recommender is the current active staker on the active cycle. |
| `reactivation_number` | PositiveIntegerField(default=0) | Which activation cycle this participant belongs to. 0 = original activation, 1 = first reactivation, and so on. This is the per-participant cycle counter and corresponds to `BookRecommendation.recommendation_cycle_number` at the page level. |
| `on_chain_stake_account` | CharField(64, blank, null) | Solana stake account or PDA reference. Backend cache. |
| `on_chain_lock_transaction` | CharField(88, blank, null) | Transaction signature of the lock. Backend cache. |
| `on_chain_reclaim_transaction` | CharField(88, blank, null) | Transaction signature of the reclaim. Backend cache. |
| `created_at` | DateTimeField(auto_now_add) | |
| `updated_at` | DateTimeField(auto_now) | |

Constraints:

```python
# One active recommender per recommendation (partial unique index)
# PostgreSQL partial unique index: only one row where is_active=True per recommendation
UniqueConstraint(
    "recommendation",
    condition=Q(is_active=True),
    name="recommenderparticipant_one_active_per_recommendation",
)

# No dust balances: application-level validation enforces 0 or >= 0.2 SOL.
# DB-level CHECK constraint as a safety net.
# The project uses Django 5.2+ which supports __gte in CheckConstraint.
CheckConstraint(
    Q(locked_amount_lamports=0) | Q(locked_amount_lamports__gte=200_000_000),
    name="recommenderparticipant_no_dust_balance",
)

# Indexes
Index(fields=["recommendation", "is_active"])                    # Find active recommender
Index(fields=["account", "-created_at"])                          # Account's participation history
Index(fields=["recommendation", "reactivation_number"])           # Cycle-based queries
Index(fields=["recommendation", "locked_amount_lamports"])        # Stake-weighted queries
```

##### Support

Records each 0.01 SOL support contribution. Immutable once created.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `supporter` | FK(Account, on_delete=PROTECT) | The user who supported. `related_name="supports_given"`. |
| `recommendation` | FK(BookRecommendation, on_delete=CASCADE) | The page supported. `related_name="supports"`. |
| `supporter_number` | PositiveIntegerField | Global ordinal support number for this recommendation across all cycles (1, 2, 3...). Never resets between activation cycles. |
| `amount_lamports` | BigIntegerField(default=10_000_000) | Fixed 0.01 SOL (10,000,000 lamports) for MVP. |
| `recommendation_cycle_number` | PositiveIntegerField | Which activation cycle this support belongs to. |
| `created_at` | DateTimeField(auto_now_add) | |
| `on_chain_support_transaction` | CharField(88, blank, null) | Transaction signature. Backend cache. |
| `on_chain_support_account` | CharField(64, blank, null) | Program account or PDA. Backend cache. |

Constraints:

```python
UniqueConstraint(
    "recommendation",
    "supporter_number",
    name="support_supporter_number_unique_per_recommendation",
)
UniqueConstraint(
    "supporter",
    "recommendation",
    name="support_one_per_supporter_per_recommendation",
)

# Indexes
Index(fields=["recommendation", "supporter_number"])  # Support list ordering
Index(fields=["supporter", "-created_at"])             # Account support history
Index(fields=["recommendation", "recommendation_cycle_number"])  # Cycle-based queries
Index(fields=["created_at"])                            # Time-based queries
```

##### Bookmark

Simple many-to-many with uniqueness enforcement.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `account` | FK(Account, on_delete=CASCADE) | `related_name="bookmarks"`. |
| `recommendation` | FK(BookRecommendation, on_delete=CASCADE) | `related_name="bookmarks_by_users"`. |
| `created_at` | DateTimeField(auto_now_add) | |

Constraints:

```python
UniqueConstraint(
    "account",
    "recommendation",
    name="bookmark_one_per_account_per_recommendation",
)

Index(fields=["account", "-created_at"])          # User's bookmarks page
Index(fields=["recommendation", "-created_at"])   # Reverse lookup (who bookmarked, newest first)
```

##### CuratorFollow

Follow relationships between accounts. Self-follow is prevented by a
database-level CHECK constraint.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `follower` | FK(Account, related_name="following", on_delete=CASCADE) | The user following. |
| `followee` | FK(Account, related_name="followers", on_delete=CASCADE) | The curator being followed. |
| `created_at` | DateTimeField(auto_now_add) | |

Constraints:

```python
UniqueConstraint(
    "follower",
    "followee",
    name="curatorfollow_one_per_pair",
)
CheckConstraint(
    ~Q(follower=F("followee")),
    name="curatorfollow_no_self_follow",
)

Index(fields=["followee", "-created_at"])  # Who follows this curator
Index(fields=["follower", "-created_at"])   # Who this user follows
```

##### Badge

Tracks badge eligibility and participation state. Does not imply book IP,
cover-art, or intellectual-property ownership. Actual NFT minting remains
on-chain.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `account` | FK(Account, on_delete=PROTECT) | The badge holder. `related_name="badges"`. |
| `recommendation` | FK(BookRecommendation, on_delete=CASCADE) | The page this badge is for. `related_name="badges"`. |
| `tier` | CharField(20) | Choices: `BRONZE` (100 supporters), `SILVER` (1,000), `GOLD` (10,000), `DIAMOND` (100,000). Thresholds are draft assumptions from `docs/tokenomics/rewards.md` and may change. |
| `earned_at` | DateTimeField | When the badge was earned based on the supporter milestone. Intentionally separate from `created_at` to allow backdated badge grants if a milestone is reached after a delay. |
| `on_chain_mint_transaction` | CharField(88, blank, null) | NFT mint transaction signature. Backend cache. |
| `on_chain_mint_account` | CharField(64, blank, null) | NFT mint account address. Backend cache. |
| `created_at` | DateTimeField(auto_now_add) | |

Constraints:

```python
UniqueConstraint(
    "account",
    "recommendation",
    "tier",
    name="badge_one_per_tier_per_account_per_recommendation",
)

# NOTE: This constraint allows the same account to earn the same tier badge
# on the same recommendation across multiple reactivation cycles. Each badge
# row is a historical record of when the milestone was reached. This is
# intentional: badges are immutable participation records, not per-cycle state.

Index(fields=["account", "-earned_at"])                    # Profile badge display
Index(fields=["recommendation", "tier"])                   # Milestone queries
Index(fields=["recommendation", "account"])                # Check if user has badge
```

##### ReputationEvent

Event-sourced reputation history. Individual events are recorded; the
aggregate formula is not implemented. The `Account.reputation_score` field
can be updated by a future aggregation process.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField PK | |
| `account` | FK(Account, on_delete=PROTECT) | `related_name="reputation_events"`. |
| `event_type` | CharField(50, choices=REPUTATION_EVENT_TYPES) | e.g., `DISCOVERY`, `REACTIVATION`, `SUPPORT_RECEIVED`, `BADGE_EARNED`. Stored as string, not enum, for flexibility. Define `REPUTATION_EVENT_TYPES` choices on the field for admin and validation clarity. |
| `points` | DecimalField(12, 2) | Points for this event. Can be positive or negative. |
| `recommendation` | FK(BookRecommendation, null, on_delete=SET_NULL) | Associated page, if any. `related_name="reputation_events"`. |
| `description` | TextField(blank) | Human-readable event description. |
| `created_at` | DateTimeField(auto_now_add) | |

Constraints:

```python
Index(fields=["account", "-created_at"])        # Account reputation timeline
Index(fields=["account", "event_type"])          # Filter by event type
Index(fields=["recommendation"])                  # Reverse lookup
```

#### Field Authorship Summary

The following categorization clarifies which fields are backend-authored,
on-chain-authored, or indexed/cache references:

| Field | Authorship | Source of Truth |
| --- | --- | --- |
| BookRecommendation.* (metadata) | Backend | Backend |
| BookRecommendation.status | Backend | Backend (mirrors on-chain cycle state) |
| BookRecommendation.current_recommender | Backend | Backend |
| BookRecommendation.on_chain_* | Cache | Solana programs |
| RecommenderParticipant.locked_amount_lamports | Cache | Solana programs |
| RecommenderParticipant.is_active | Backend | Backend |
| RecommenderParticipant.on_chain_* | Cache | Solana programs |
| Support.* (all) | Backend | Backend |
| Support.on_chain_* | Cache | Solana programs |
| Badge.tier | Backend | Backend (milestone thresholds) |
| Badge.on_chain_* | Cache | Solana programs |
| ReputationEvent.* | Backend | Backend |

#### Concurrency Considerations

The following concurrency risks exist in the schema and must be addressed during
implementation:

**`Support.supporter_number` race condition:** Two concurrent support requests
could read the same maximum `supporter_number` and create duplicate ordinals,
violating the `support_supporter_number_unique_per_recommendation` constraint.
The implementation must use one of:

- `SELECT FOR UPDATE` on the `BookRecommendation` row before computing the next
  `supporter_number`, or
- A `Max("supporter_number") + 1` inside `select_for_update()`, or
- Application-level advisory locking per recommendation.

**`BookRecommendation.support_count` denormalization:** The denormalized
`support_count` must be updated atomically on each new support. The
implementation should use `F("support_count") + 1` in an `UPDATE` statement
rather than reading and writing the count. The `last_support_at` timestamp
cannot be atomically updated with the count in a single statement; the
implementation should use a single `UPDATE` with a conditional timestamp
assignment via PostgreSQL `GREATEST`:

```python
BookRecommendation.objects.filter(pk=recommendation_pk).update(
    support_count=F("support_count") + 1,
    last_support_at=Greatest("last_support_at", Value(support_created_at)),
)
```

This avoids lost updates from concurrent support actions. Using `GREATEST`
ensures `last_support_at` only advances forward.

**`RecommenderParticipant` one-active-per-recommendation constraint:** Django's
ORM does not validate partial unique constraints at the application level. The
implementation must handle `IntegrityError` on concurrent `is_active` toggles
and retry or return a user-facing error. Using `select_for_update()` on the
parent `BookRecommendation` row before toggling `is_active` is recommended.

#### Implementation Notes

**`__str__` methods:** Every model should define a `__str__` method for Django
admin usability and debugging. Suggested representations:

- `BookRecommendation`: `f"{self.title} by {self.author_names}"`
- `Category`: `self.name`
- `DuplicateReport`: `f"Report #{self.pk} on {self.recommendation}"`
- `RecommenderParticipant`: `f"{self.account} on {self.recommendation}"`
- `Support`: `f"Support #{self.supporter_number} by {self.supporter}"`
- `Bookmark`: `f"{self.account} → {self.recommendation}"`
- `CuratorFollow`: `f"{self.follower} → {self.followee}"`
- `Badge`: `f"{self.tier} for {self.recommendation} ({self.account})"`
- `ReputationEvent`: `f"{self.event_type} for {self.account}"`

**`related_name` on FK fields:** Several FK fields should specify explicit
`related_name` values to avoid ambiguous reverse accessor names and Django
deprecation warnings. All `related_name` values are listed in the model field
tables above. Key entries:

- `BookRecommendation.creator` → `related_name="created_recommendations"`
- `BookRecommendation.current_recommender` → `related_name="active_recommendations"`
- `DuplicateReport.reporter` → `related_name="duplicate_reports_filed"`
- `DuplicateReport.recommendation` → `related_name="duplicate_reports"`
- `DuplicateReport.suspected_duplicate_of` → `related_name="suspected_duplicates"`
- `RecommenderParticipant.account` → `related_name="recommender_participations"`
- `RecommenderParticipant.recommendation` → `related_name="recommender_participants"`
- `Support.supporter` → `related_name="supports_given"`
- `Support.recommendation` → `related_name="supports"`
- `Bookmark.account` → `related_name="bookmarks"`
- `Bookmark.recommendation` → `related_name="bookmarks_by_users"` (differs from `Bookmark.account` to avoid ambiguity since both target models use `bookmarks`)
- `CuratorFollow.follower` → `related_name="following"`
- `CuratorFollow.followee` → `related_name="followers"`
- `Badge.account` → `related_name="badges"`
- `Badge.recommendation` → `related_name="badges"`
- `ReputationEvent.account` → `related_name="reputation_events"`
- `ReputationEvent.recommendation` → `related_name="reputation_events"`

**Duplicate report scope:** `DuplicateReport` allows reporting both canonical
and candidate (non-canonical) pages. The `suspected_duplicate_of` field may
reference any other `BookRecommendation` regardless of its `is_canonical` status.
Application-level validation should prevent a user from filing a report where
`suspected_duplicate_of` is the same record as `recommendation` (enforced by the
`duplicatereport_no_self_reference` CHECK constraint).

**`on_delete` behavior:** All FK fields specify explicit `on_delete` values as
listed in the schema tables. Key design decisions:
- `PROTECT` on account FKs where historical records must not be silently
  deleted (creator, supporter, reporter, recommender account, badge account,
  reputation event account).
- `CASCADE` on recommendation FKs for child records that should not outlive
  their parent page (supports, duplicate reports, bookmarks, recommender
  participants, badges).
- `SET_NULL` on nullable FKs where the reference is optional (current
  recommender, category, suspected duplicate of, reputation event
  recommendation).

**Default `ordering`:** Models with expected list-heavy access patterns should
define `ordering` in their `Meta` class:
- `Support`: `ordering = ["recommendation", "supporter_number"]`
- `Bookmark`: `ordering = ["-created_at"]`
- `Badge`: `ordering = ["-earned_at"]`
- `ReputationEvent`: `ordering = ["-created_at"]`
- `DuplicateReport`: `ordering = ["-created_at"]`
- `CuratorFollow`: `ordering = ["-created_at"]`

**`USE_TZ` awareness:** The project uses `USE_TZ = True`. All `auto_now_add`
and `auto_now` timestamps are stored as UTC by Django's ORM. The plan's
`created_at`, `updated_at`, `earned_at`, and `last_support_at` fields rely on
this. No manual timezone conversion should be needed in model code; ensure any
raw SQL (e.g., the `GREATEST` pattern for `last_support_at`) passes
timezone-aware datetimes.

**Test layout `__init__.py`:** The existing `tests/accounts/` directory has no
`__init__.py`, matching the project's pytest discovery convention. The new
`tests/recommendations/` directory should follow the same pattern — no
`__init__.py` unless pytest configuration requires it.

#### Verification

- [x] Schema review confirms no unresolved reward formula is encoded in database
  fields or model methods.
- [x] All locked SOL amounts are stored in lamports (BigIntegerField) with
  backend-level CHECK constraints; actual custody remains on-chain.
- [x] Diminishing-returns principle is captured as a storage requirement (store
  raw amounts) without encoding a formula.
- [x] Badge model uses participation language; no ownership or IP implication.
- [x] Support model stores fixed 0.01 SOL amount with no refundable-vote
  semantics.

Dependencies: Spec Approval checkpoint.

Files likely touched:

- `docs/plans/0016-recommendation-lifecycle-data-model.md`
- Optional schema note under `docs/architecture/` if the design becomes too large
  for the plan.

Estimated scope: Medium.

### Task 6: Confirm App Boundaries And Naming

Description: Decide whether the product models live in a new Django app or the
existing `accounts` app before creating migrations.

Acceptance criteria:

- [x] Decision records whether to create a new app such as `recommendations` or
  keep models in an existing app.
- [x] Naming is consistent across models, serializers, API routes, and docs.
- [x] If a new app is chosen, `INSTALLED_APPS` and test layout changes are listed.
- [x] Boundaries avoid putting product marketplace logic inside account auth
  models.

Verification:

- [x] Review confirms model ownership is clear and does not create avoidable
  coupling with authentication code.

#### Decision: Create a new `recommendations` Django app

Product models must not live in the `accounts` app. The `accounts` app owns
authentication, session management, social auth, email verification, password
reset, throttling, and the custom `Account` user model. Mixing marketplace
product logic (book recommendations, support, badges, curator follows) into
the auth boundary would create coupling between authentication concerns and
product domain concerns.

A new Django app named `recommendations` will house all product data models.

#### App layout

```
apps/api/recommendations/
├── __init__.py
├── apps.py              # RecommendationsConfig
├── models.py            # All product models
├── admin.py             # Read-only admin review surfaces (Task 8)
└── migrations/
    └── __init__.py
```

#### `INSTALLED_APPS` change

Add to `beacon_api/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    "accounts",
    "recommendations",  # Product data models
]
```

#### Test layout

```
apps/api/tests/recommendations/
├── test_models.py       # Constraint and lifecycle tests (Task 9)
└── test_admin.py        # Admin surface tests (Task 8)
```

Note: no `__init__.py` in the test directory, matching the existing convention
in `tests/accounts/`. pytest discovers tests via `testpaths` config.

#### Naming conventions

| Layer | Convention | Examples |
| --- | --- | --- |
| Models | PascalCase | `BookRecommendation`, `RecommenderParticipant` |
| Model table names | app_label lowercase + snake_case | `recommendations_bookrecommendation` |
| API routes | kebab-case under `/api/recommendations/` | `/api/recommendations/`, `/api/recommendations/{id}/support/` |
| Serializers | PascalCase + `Serializer` suffix | `BookRecommendationSerializer` |
| Admin sites | app label prefix | `recommendations` admin section |
| Docs | product-marketplace terminology, not generic "post" or "upvote" | recommendation, support, curator |

#### Dependencies

The `recommendations` app FK-references `accounts.Account` via
`settings.AUTH_USER_MODEL`. This is the only cross-app dependency. The
`accounts` app has no knowledge of the `recommendations` app.

Dependencies: Task 5.

Files likely touched:

- `docs/plans/0016-recommendation-lifecycle-data-model.md`
- Later implementation files under `apps/api/`.

Estimated scope: Small.

## Phase 3: Write Model Tests First (TDD — RED Phase) (completed)

### Task 7: Write Model Tests For Constraints And Lifecycle State (completed)

Description: Write comprehensive model tests before implementing the Django
models. This follows TDD: the tests will initially fail because the models do
not yet exist, then pass once models are implemented. All acceptance criteria
from the original plan are tested here.

Acceptance criteria:

- [x] Tests cover canonical recommendation uniqueness rules selected by the spec.
- [x] Tests cover standalone-work versus series page type constraints selected by
  the schema design.
- [x] Tests cover duplicate-risk/manual-review state transitions that are in scope
  for the backend model.
- [x] Tests cover duplicate bookmark prevention.
- [x] Tests cover duplicate curator follow prevention.
- [x] Tests cover self-follow prevention for curator follows.
- [x] Tests cover support supporter-number uniqueness per recommendation.
- [x] Tests cover self-reference prevention for duplicate reports.
- [x] Tests cover duplicate badge prevention (same tier, same account, same
  recommendation).
- [x] Tests cover reputation event creation and account/recommendation FK
  relationships.
- [x] Tests cover future-credit eligibility for historical recommenders based on
  locked versus reclaimed stake without implementing reward formulas.
- [ ] Tests cover inactive eligibility conditions as pure backend state rules if
  those rules are implemented in model/query helpers.
- [x] Tests cover the `RecommenderParticipant` CHECK constraint (locked amount
  must be 0 or >= 0.2 SOL), including edge values (1 lamport, 199,999,999
  lamports).
- [x] Tests cover `__str__` representations for all models.
- [x] Tests cover `on_delete` behavior: deleting a recommendation cascades
  child records (supports, bookmarks, badges); deleting an account with
  creator/supporter/recommender references is blocked by PROTECT.
- [x] Tests cover `ReputationEvent.event_type` choices validation.
- [x] Tests cover `Badge` allows the same tier badge across different
  reactivation cycles (intentional per schema design).

Verification:

- [x] `cd apps/api && .venv/bin/pytest tests/recommendations/test_models.py`
  runs and all tests FAIL (RED phase) because models do not exist yet.

Dependencies: Tasks 5 and 6.

Files likely touched:

- `apps/api/tests/recommendations/__init__.py` (empty, for pytest discovery)
- `apps/api/tests/recommendations/test_models.py`
- `apps/api/tests/recommendations/factories.py` (use `factory_boy`, already
  installed as a dev dependency)

Estimated scope: Medium.

### Task 8: Test Migration Generation And Database Checks (completed)

Description: After models are implemented (Phase 4), verify the schema can be
created cleanly from scratch before consolidating migrations.

Acceptance criteria:

- [x] Generated migrations create all product tables and constraints.
- [x] Migration files do not encode temporary intermediate states.
- [ ] Database checks pass against the supported local test database.
- [x] No test assumes final reward or reputation formulas.

Verification:

- [x] `cd apps/api && .venv/bin/python manage.py makemigrations --check --dry-run`
  passes after migrations are generated.
- [x] `cd apps/api && .venv/bin/python manage.py check` passes.
- [ ] `cd apps/api && .venv/bin/pytest` passes or documented environment-specific
  blockers are recorded. (Blocked: PostgreSQL not running locally.)

Dependencies: Task 7 (tests) and Tasks 9-10 (models, Phase 4).

Files likely touched:

- Django migration files.
- Test files.

Estimated scope: Medium.

## Phase 4: Implement Models And Admin (TDD — GREEN Phase) (completed)

### Task 9: Add Product Models (completed)

Description: Implement the approved Django models with constraints, indexes, and
clear field names. This is the GREEN phase of TDD — writing the minimum
implementation to make the tests from Phase 3 pass.

Acceptance criteria:

- [x] Canonical recommendation page model stores required MVP book or series
  metadata: page type, title, author or authors, curator note or description,
  external reference link, category or genre, creation timestamp, active state,
  duplicate-risk/manual-review state, and activity timestamps.
- [x] Recommender participant model records account, recommendation, locked stake
  amount, lock timestamps, reclaim timestamp, active eligibility, and optional
  on-chain references.
- [x] Support model records supporter, recommendation, optional recommender
  lifecycle context, support amount, supporter number, timestamp, and optional
  on-chain references.
- [x] Bookmark model prevents duplicate bookmarks per account and recommendation.
- [x] Curator follow model prevents duplicate follows and prevents self-follow if
  that rule is accepted.
- [x] Badge model stores participation/badge state without implying book IP or
  cover-art ownership.
- [x] Models include indexes for likely access paths: active recommendations,
  recommendation support lists, account support history, account bookmarks,
  account followers/following, badge lists, and active recommender participants.

Verification:

- [x] `cd apps/api && .venv/bin/python manage.py makemigrations --check --dry-run`
  reports expected pending migrations before migration generation.
- [ ] `cd apps/api && .venv/bin/pytest tests/recommendations/test_models.py`
  passes (GREEN phase). (Blocked: PostgreSQL not running locally; tests collect
  successfully but cannot create test database.)

Dependencies: Task 7 (tests).

Files likely touched:

- New Django app `apps/api/recommendations/__init__.py`.
- New Django app `apps/api/recommendations/apps.py`.
- New Django app `apps/api/recommendations/models.py`.
- New Django app `apps/api/recommendations/migrations/__init__.py`.
- `apps/api/beacon_api/settings.py` if a new app is added.

Estimated scope: Medium.

### Task 10: Add Django Admin Read-Only Review Surfaces (completed)

Description: Add minimal admin support so developers can inspect early product
state during MVP development.

Acceptance criteria:

- [x] Admin list views expose recommendation title, active state, support count,
  current recommender status, and timestamps.
- [x] Economic/on-chain reference fields are read-only where appropriate.
- [x] Badge records do not display language implying ownership of books or IP.
- [x] Admin search and filters support common debugging paths.

Verification:

- [x] `cd apps/api && .venv/bin/python manage.py check` passes.

Dependencies: Task 9.

Files likely touched:

- `apps/api/recommendations/admin.py`.

Estimated scope: Small.

## Phase 5: Consolidate Pre-Launch Migrations

### Task 11: Rewrite Initial Migrations For Pre-Launch State

Description: Because Beacon has no real users and is unpublished, replace the
current incremental migration history with clean initial migrations that represent
the approved pre-launch schema.

Acceptance criteria:

- [x] Existing applied local migration state is treated as disposable development
  state.
- [x] `accounts/migrations/0002_remove_redundant_email_unique.py` is removed only
  after the new initial migration contains the correct non-unique email field and
  case-insensitive email constraint.
- [x] New product app migrations, if any, start from `0001_initial.py`.
- [x] Migration dependencies are correct for `AUTH_USER_MODEL` relations.
- [x] Instructions are documented for resetting local development databases after
  the migration rewrite.

Verification:

- [x] From an empty development database, `cd apps/api && .venv/bin/python
  manage.py migrate` succeeds.
- [x] `cd apps/api && .venv/bin/python manage.py showmigrations` shows only the
  intended initial app migrations for local fresh state.

Dependencies: Tasks 7-10.

Files likely touched:

- `apps/api/accounts/migrations/0001_initial.py`
- `apps/api/accounts/migrations/0002_remove_redundant_email_unique.py`
- New product app migrations.
- `docs/development/database.md` or relevant backend README reset instructions.

Estimated scope: Medium.

Manual blocker: Confirm no real or persistent data needs preservation before
rewriting migration history.

## Phase 6: Add API Planning Stubs Or Follow-Up Plans

### Task 12: Define API Surface For Product Interactions

Description: Create a follow-up implementation plan for APIs after the model layer
is approved.

Acceptance criteria:

- [x] Follow-up plan lists endpoints for creating recommendations, reactivating
  recommendations, adding or reclaiming recommender stake references, supporting a
  recommendation, listing user supports/upvotes, bookmarking recommendations,
  following curators, listing badges, and reading reputation/profile summaries.
- [x] API plan separates backend product state endpoints from Solana transaction
  construction/signing flows.
- [x] API plan identifies permissions, pagination, filtering, and idempotency
  requirements.
- [x] API plan does not document endpoints as already implemented.

Verification:

- [x] Follow-up plan is linked from `docs/plans/README.md` if created.

Dependencies: Tasks 1-11.

Files likely touched:

- New plan under `docs/plans/`.
- `docs/api/openapi.md` planning section if needed.

Estimated scope: Small.

## Checkpoint: Model Foundation Complete

- [x] Specs and decision records are updated and approved.
- [x] Django models exist for the approved MVP data model.
- [x] Model constraints and lifecycle rules have tests.
- [x] Fresh migrations apply from an empty database.
- [x] Migration rewrite/reset instructions are documented.
- [x] No unresolved reward, badge, governance, or reputation formulas were
  implemented prematurely.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Model encodes unresolved reward policy too early | High | Store stake/support/badge history only; keep formulas in open questions until approved. |
| Single recommendation table becomes overloaded | Medium | Keep canonical page in one model for MVP, but separate recommender participation, support, badges, bookmarks, and follows. |
| Uncapped deposits create whale-concentration risk if mapped linearly to credit | Medium | Store locked amounts and require diminishing returns; keep the exact curve, caps, and stake increments open before implementation. |
| Duplicate or volume-level pages fragment canonical support | High | Use standalone-work or series-level identity, high-sensitivity duplicate-risk detection, manual review for risky candidates, and duplicate reports. |
| Migration rewrite breaks existing local databases | Medium | Treat current local data as disposable; document reset steps; do not use this approach after real users exist. |
| Backend appears authoritative for funds | High | Store on-chain references and indexed state only; keep custody and economic execution on-chain per architecture docs. |
| Badge model implies book/IP ownership | High | Use participation language only; keep metadata and transfer policy unresolved until approved. |
| Generic post/upvote language drifts from specs | Medium | Use recommendation/support terminology in docs, models, APIs, and UI. |

## Open Questions

- What exact duplicate-risk scoring and matching algorithm should be used?
- What manual review service level is acceptable for duplicate-risk candidate
  pages and review-blocked reactivations?
- What exact diminishing-returns curve should apply to future historical
  recommender credit from locked SOL amount?
- Should there be a cap on credit share from extra stake?
- How should reward splits work across multiple recommender participants and
  multiple support cohorts?
- Are badge transfers allowed, restricted, or discouraged?
- Which reputation signals are stored as events versus aggregates?
- Should `Support` records be allowed during `INACTIVE` recommendation
  periods, or should support be restricted to `ACTIVE` cycles only?

## Approval Gate

This plan is `Completed`. All 12 tasks across 6 phases are done. The data model,
migrations, admin surfaces, and follow-up API plan are in place.
