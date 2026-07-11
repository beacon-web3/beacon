# Recommendation Lifecycle Data Model

## Status

Draft

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

## Phase 1: Update Specs, Assumptions, And Decisions

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

- [ ] `docs/architecture/system-design.md` lists canonical recommendation pages,
  recommender participants, support history, bookmarks, curator follows, badge
  history, and reputation history as backend product concepts.
- [ ] Architecture docs state that economic custody, stake locks, support
  transfers, and reward release remain on-chain or on-chain-indexed when
  implemented.
- [ ] `docs/api/openapi.md` receives a planning note or future endpoint section
  for recommendation lifecycle APIs if useful.
- [ ] No API endpoint is documented as implemented before code exists.

Verification:

- [ ] Documentation review confirms architecture, API, and product docs use the
  same vocabulary.

Dependencies: Tasks 1-3.

Files likely touched:

- `docs/architecture/system-design.md`
- `docs/api/openapi.md`

Estimated scope: Small.

## Checkpoint: Spec Approval

Do not start model implementation until this checkpoint is complete.

- [ ] Product specs reflect the new recommendation lifecycle.
- [ ] Assumptions and open questions capture unresolved policy.
- [ ] Decision record is added and indexed.
- [ ] Architecture docs define off-chain versus on-chain responsibility.
- [ ] Human review confirms the product direction is ready for schema work.

## Phase 2: Design Backend Data Model

### Task 5: Draft Django Model Schema

Description: Draft the Django model structure in the plan or a schema design note
before editing `models.py`.

Acceptance criteria:

- [ ] Proposed schema includes `BookRecommendation` or the chosen canonical page
  model.
- [ ] Proposed schema identifies whether each canonical page represents a
  standalone work or recognized series.
- [ ] Proposed schema includes duplicate-risk/manual-review state for candidate
  pages and a way to record duplicate reports.
- [ ] Proposed schema includes a recommender participant/stake-position model for
  active and historical recommender credit.
- [ ] Proposed schema includes support/upvote history with fixed `0.01 SOL` MVP
  contribution accounting.
- [ ] Proposed schema includes bookmarks.
- [ ] Proposed schema includes curator follows.
- [ ] Proposed schema includes badge/NFT history or eligibility cache.
- [ ] Proposed schema includes enough fields to support reputation aggregation
  later without defining the final formula.
- [ ] Proposed schema identifies all uniqueness constraints and indexes.
- [ ] Proposed schema identifies fields that are authoritative on-chain versus
  backend cache/reference fields.

Verification:

- [ ] Schema review confirms no unresolved reward formula is encoded in database
  fields or model methods.

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

- [ ] Decision records whether to create a new app such as `recommendations` or
  keep models in an existing app.
- [ ] Naming is consistent across models, serializers, API routes, and docs.
- [ ] If a new app is chosen, `INSTALLED_APPS` and test layout changes are listed.
- [ ] Boundaries avoid putting product marketplace logic inside account auth
  models.

Verification:

- [ ] Review confirms model ownership is clear and does not create avoidable
  coupling with authentication code.

Dependencies: Task 5.

Files likely touched:

- `docs/plans/0016-recommendation-lifecycle-data-model.md`
- Later implementation files under `apps/api/`.

Estimated scope: Small.

## Phase 3: Implement Models And Admin Foundation

### Task 7: Add Product Models

Description: Implement the approved Django models with constraints, indexes, and
clear field names.

Acceptance criteria:

- [ ] Canonical recommendation page model stores required MVP book or series
  metadata: page type, title, author or authors, curator note or description,
  external reference link, category or genre, creation timestamp, active state,
  duplicate-risk/manual-review state, and activity timestamps.
- [ ] Recommender participant model records account, recommendation, locked stake
  amount, lock timestamps, reclaim timestamp, active eligibility, and optional
  on-chain references.
- [ ] Support model records supporter, recommendation, optional recommender
  lifecycle context, support amount, supporter number, timestamp, and optional
  on-chain references.
- [ ] Bookmark model prevents duplicate bookmarks per account and recommendation.
- [ ] Curator follow model prevents duplicate follows and prevents self-follow if
  that rule is accepted.
- [ ] Badge model stores participation/badge state without implying book IP or
  cover-art ownership.
- [ ] Models include indexes for likely access paths: active recommendations,
  recommendation support lists, account support history, account bookmarks,
  account followers/following, badge lists, and active recommender participants.

Verification:

- [ ] `cd apps/api && .venv/bin/python manage.py makemigrations --check --dry-run`
  reports expected pending migrations before migration generation.
- [ ] Model tests are planned before migration finalization.

Dependencies: Tasks 5 and 6.

Files likely touched:

- New or existing Django app `models.py`.
- New or existing Django app `apps.py`.
- `apps/api/beacon_api/settings.py` if a new app is added.

Estimated scope: Medium.

### Task 8: Add Django Admin Read-Only Review Surfaces

Description: Add minimal admin support so developers can inspect early product
state during MVP development.

Acceptance criteria:

- [ ] Admin list views expose recommendation title, active state, support count,
  current recommender status, and timestamps.
- [ ] Economic/on-chain reference fields are read-only where appropriate.
- [ ] Badge records do not display language implying ownership of books or IP.
- [ ] Admin search and filters support common debugging paths.

Verification:

- [ ] `cd apps/api && .venv/bin/python manage.py check` passes.

Dependencies: Task 7.

Files likely touched:

- New or existing Django app `admin.py`.

Estimated scope: Small.

## Phase 4: Add Model Tests

### Task 9: Test Constraints And Lifecycle State

Description: Add model tests for uniqueness, relationships, and active/inactive
state transitions that can be tested without Solana integration.

Acceptance criteria:

- [ ] Tests cover canonical recommendation uniqueness rules selected by the spec.
- [ ] Tests cover standalone-work versus series page type constraints selected by
  the schema design.
- [ ] Tests cover duplicate-risk/manual-review state transitions that are in scope
  for the backend model.
- [ ] Tests cover duplicate bookmark prevention.
- [ ] Tests cover duplicate curator follow prevention.
- [ ] Tests cover support supporter-number uniqueness per recommendation.
- [ ] Tests cover future-credit eligibility for historical recommenders based on
  locked versus reclaimed stake without implementing reward formulas.
- [ ] Tests cover inactive eligibility conditions as pure backend state rules if
  those rules are implemented in model/query helpers.

Verification:

- [ ] `cd apps/api && .venv/bin/pytest tests/...` passes for targeted model tests.

Dependencies: Tasks 7 and 8.

Files likely touched:

- `apps/api/tests/.../test_models.py`
- Test factories or helpers if the project adds them.

Estimated scope: Medium.

### Task 10: Test Migration Generation And Database Checks

Description: Verify the schema can be created cleanly from scratch before
consolidating migrations.

Acceptance criteria:

- [ ] Generated migrations create all product tables and constraints.
- [ ] Migration files do not encode temporary intermediate states.
- [ ] Database checks pass against the supported local test database.
- [ ] No test assumes final reward or reputation formulas.

Verification:

- [ ] `cd apps/api && .venv/bin/python manage.py makemigrations --check --dry-run`
  passes after migrations are generated.
- [ ] `cd apps/api && .venv/bin/python manage.py check` passes.
- [ ] `cd apps/api && .venv/bin/pytest` passes or documented environment-specific
  blockers are recorded.

Dependencies: Task 9.

Files likely touched:

- Django migration files.
- Test files.

Estimated scope: Medium.

## Phase 5: Consolidate Pre-Launch Migrations

### Task 11: Rewrite Initial Migrations For Pre-Launch State

Description: Because Beacon has no real users and is unpublished, replace the
current incremental migration history with clean initial migrations that represent
the approved pre-launch schema.

Acceptance criteria:

- [ ] Existing applied local migration state is treated as disposable development
  state.
- [ ] `accounts/migrations/0002_remove_redundant_email_unique.py` is removed only
  after the new initial migration contains the correct non-unique email field and
  case-insensitive email constraint.
- [ ] New product app migrations, if any, start from `0001_initial.py`.
- [ ] Migration dependencies are correct for `AUTH_USER_MODEL` relations.
- [ ] Instructions are documented for resetting local development databases after
  the migration rewrite.

Verification:

- [ ] From an empty development database, `cd apps/api && .venv/bin/python
  manage.py migrate` succeeds.
- [ ] `cd apps/api && .venv/bin/python manage.py showmigrations` shows only the
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

- [ ] Follow-up plan lists endpoints for creating recommendations, reactivating
  recommendations, adding or reclaiming recommender stake references, supporting a
  recommendation, listing user supports/upvotes, bookmarking recommendations,
  following curators, listing badges, and reading reputation/profile summaries.
- [ ] API plan separates backend product state endpoints from Solana transaction
  construction/signing flows.
- [ ] API plan identifies permissions, pagination, filtering, and idempotency
  requirements.
- [ ] API plan does not document endpoints as already implemented.

Verification:

- [ ] Follow-up plan is linked from `docs/plans/README.md` if created.

Dependencies: Tasks 1-11.

Files likely touched:

- New plan under `docs/plans/`.
- `docs/api/openapi.md` planning section if needed.

Estimated scope: Small.

## Checkpoint: Model Foundation Complete

- [ ] Specs and decision records are updated and approved.
- [ ] Django models exist for the approved MVP data model.
- [ ] Model constraints and lifecycle rules have tests.
- [ ] Fresh migrations apply from an empty database.
- [ ] Migration rewrite/reset instructions are documented.
- [ ] No unresolved reward, badge, governance, or reputation formulas were
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
- Which fields are backend-authored, on-chain-authored, or indexed from Solana
  events?

## Approval Gate

This plan should remain `Draft` until Phase 1 is reviewed. Implementation should
not start until the product spec and decision-record updates resolve the core
recommendation lifecycle vocabulary and active-credit rules.
