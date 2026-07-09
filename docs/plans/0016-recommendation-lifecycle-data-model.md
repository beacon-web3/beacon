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
first-discoverer model to a stake-backed active recommender model:

- A book keeps one canonical Beacon recommendation page.
- Any user who stakes the required SOL can recommend or reactivate that book.
- Active recommendation credit belongs only to recommender participants with
  currently locked stake.
- Active credit can be split by locked SOL amount when multiple recommenders
  have active stake.
- If all stake is withdrawn and no new support arrives for a defined inactivity
  window, such as three months, the recommendation can become inactive.
- An inactive recommendation can be reactivated by another recommender staking
  SOL.
- Historical discovery, activation, support, badge, and reputation records remain
  visible even when current active credit changes.
- The exact reward split formula is intentionally unresolved and must not be
  implemented in this plan.

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
- `docs/api/openapi.md`
- `apps/api/accounts/models.py`
- `apps/api/accounts/migrations/`

## Objective

Define and implement the first backend product data model for Beacon's canonical
book recommendation lifecycle while keeping economic policy unresolved where the
specs are still draft.

The implementation should support:

- One canonical recommendation page per book identity.
- Active/inactive lifecycle for recommendations.
- Multiple recommender participants over time.
- Stake-backed active recommender credit tracking.
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
- The recommendation contains both book metadata and Beacon-specific
  recommendation state for MVP simplicity.
- A recommendation can become inactive when all active stake is withdrawn and no
  support/upvote has arrived for the configured inactivity window.
- The initial inactivity window is a draft assumption, for example three months,
  not a finalized economic parameter unless explicitly accepted.
- An inactive recommendation can be reactivated by any eligible recommender who
  stakes at least the required minimum.
- Active recommender credit is based on currently locked stake, not permanent
  first-mover ownership.
- Historical recommender participation remains visible even when active credit is
  zero.
- The exact reward formula for multiple recommender participants remains an open
  question and is not implemented.

## Architecture Decisions

- Use a single canonical recommendation page model for MVP instead of separate
  neutral `Book` and `Recommendation` tables.
- Add a separate recommender participation/stake table so one canonical page can
  have multiple recommender activation periods and stake positions over time.
- Link support/upvotes to the canonical recommendation and, when relevant, the
  active lifecycle period for later reward analysis.
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

- [ ] `docs/product/mvp.md` describes one canonical page per book with active and
  inactive states.
- [ ] `docs/product/mvp.md` explains that reactivation preserves the canonical
  page, historical supports, badges, and recommender history.
- [ ] `docs/product/user-stories.md` includes user-facing behavior for creating,
  supporting, bookmarking, following curators, viewing upvote/support history,
  viewing badges, and viewing reputation.
- [ ] Product copy avoids describing support as a refundable vote or guaranteed
  investment return.
- [ ] Specs distinguish active recommender credit from historical discovery
  history.

Verification:

- [ ] Documentation review confirms there is no conflict between `mvp.md`,
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

- [ ] `docs/product/assumptions.md` adds a draft assumption for the recommendation
  inactivity window, such as three months.
- [ ] `docs/product/assumptions.md` adds a draft assumption for stake-weighted
  active recommender credit if approved as the working model.
- [ ] `docs/product/open-questions.md` records unresolved questions about reward
  split formulas across multiple recommender participants.
- [ ] `docs/product/open-questions.md` records unresolved questions about stake
  caps, minimum stake additions, whale concentration, inactivity timing, and
  active-credit eligibility.
- [ ] Any unresolved badge transfer, metadata, or minting policy remains open
  rather than being decided by model code.

Verification:

- [ ] Documentation review confirms all unresolved tokenomics and badge mechanics
  remain listed as draft assumptions or open questions.

Dependencies: Task 1.

Files likely touched:

- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md` if stake lifecycle wording needs alignment.

Estimated scope: Medium.

### Task 3: Add Decision Record For Stake-Backed Recommendation Lifecycle

Description: Add an ADR/product decision record documenting why Beacon is using a
canonical recommendation page with active stake-backed recommender credit instead
of a permanent first-discoverer-only model.

Acceptance criteria:

- [ ] New decision record is added under `docs/decisions/` with the next
  sequential ID.
- [ ] Decision status is `Proposed` unless the product decision is explicitly
  accepted before writing.
- [ ] Decision explains the active recommender credit model, historical discovery
  history, reactivation behavior, and unresolved reward formula.
- [ ] Alternatives considered include permanent first-discoverer credit, separate
  `Book` and `Recommendation` tables, and generic posts/upvotes.
- [ ] `docs/decisions/README.md` is updated.

Verification:

- [ ] Decision record links to the relevant specs and does not contradict product
  guardrails.

Dependencies: Tasks 1 and 2.

Files likely touched:

- `docs/decisions/0011-stake-backed-recommendation-lifecycle.md`
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
- [ ] Proposed schema includes a recommender participant/stake-position model for
  active and historical recommender credit.
- [ ] Proposed schema includes support/upvote history.
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

- [ ] Canonical recommendation page model stores required MVP book metadata:
  title, author, curator note or description, external reference link, category
  or genre, creation timestamp, active state, and activity timestamps.
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
- [ ] Tests cover duplicate bookmark prevention.
- [ ] Tests cover duplicate curator follow prevention.
- [ ] Tests cover support supporter-number uniqueness per recommendation.
- [ ] Tests cover active recommender credit eligibility based on locked versus
  reclaimed stake without implementing reward formulas.
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
| Stake-weighted credit creates whale concentration | Medium | Record caps or nonlinear weighting as open questions before implementation. |
| Migration rewrite breaks existing local databases | Medium | Treat current local data as disposable; document reset steps; do not use this approach after real users exist. |
| Backend appears authoritative for funds | High | Store on-chain references and indexed state only; keep custody and economic execution on-chain per architecture docs. |
| Badge model implies book/IP ownership | High | Use participation language only; keep metadata and transfer policy unresolved until approved. |
| Generic post/upvote language drifts from specs | Medium | Use recommendation/support terminology in docs, models, APIs, and UI. |

## Open Questions

- What exact inactivity window should move a recommendation from active to
  inactive?
- Is active recommender credit always linear by locked SOL amount?
- Should there be a cap on credit share from extra stake?
- Can previous recommenders add stake while another recommender is active?
- What minimum stake is required to join or rejoin active recommender credit?
- Should inactive recommendations require moderation review before reactivation?
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
