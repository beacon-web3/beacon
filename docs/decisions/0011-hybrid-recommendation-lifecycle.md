# 0011: Hybrid Recommendation Lifecycle

## Status

Accepted

## Date

2026-07-09

## Context

Beacon needs one canonical page per standalone book work or recognized series
while still allowing recommendation activity to evolve over time. The original
MVP language gave permanent
discoverer credit to the first valid curator, but the backend data-model plan
introduced active stake-backed recommendation cycles and reactivation. Those
ideas conflicted until the product lifecycle was clarified.

The lifecycle must preserve Beacon's discovery and reputation primitive without
turning every active book into an open staking race that any new user can dilute
immediately.

## Decision

Beacon will use a hybrid recommendation lifecycle:

- Each standalone book work or recognized series has one permanent canonical
  Beacon page.
- The first valid recommender receives permanent historical discoverer credit.
- At any moment, a page has at most one active recommendation cycle.
- A new user can lock the required base SOL to activate or reactivate a
  recommendation only when the current recommendation cycle is inactive.
- The user who activates or reactivates a recommendation becomes part of that
  page's historical recommender set.
- The original discoverer and prior reactivators may lock additional SOL at any
  time to increase their share of future upvote/support credit.
- New users who have never activated or reactivated that page cannot stake into
  it while it is active; they must wait for deactivation.
- Additional locked SOL affects future credit allocation only. It must not
  rewrite past support credit, badges, discoverer credit, or reputation history.
- The exact credit-share and reward formulas remain unresolved pending
  tokenomics simulation and abuse review.

This decision amends `0002-canonical-book-pages.md`. The permanent canonical page
and immutable discoverer credit remain accepted, but later reactivation and
historical recommender stake rights are now part of the product model.

`0012-canonical-work-series-identity.md` further specifies that the canonical MVP
page can represent a standalone book work or a recognized series.

`0013-recommendation-inactivity-window.md` specifies the MVP inactivity rule as
zero locked recommender SOL plus 90 days with no new support.

## Alternatives Considered

### Permanent discoverer only

- Pros: Simple, strongly reinforces first-discovery reputation, easy to explain.
- Cons: Too static; does not support reactivation or later recommender activity
  when the original recommendation becomes inactive.
- Rejected as incomplete.

### Fully open active staking

- Pros: Maximizes ongoing participation and creates a simple stake-weighted pool.
- Cons: Lets any new user dilute the active recommender immediately, weakening
  the early-discovery story and increasing whale-concentration risk.
- Rejected for MVP lifecycle semantics.

### Separate competing recommendation pages per book

- Pros: Lets multiple users compete with different recommendation narratives.
- Cons: Fragments support, reputation, and reward eligibility; contradicts the
  canonical page model.
- Rejected for MVP.

## Consequences

- Product copy must distinguish permanent historical discoverer credit, active
  recommendation status, historical recommender membership, and future
  upvote/support credit share.
- Backend models should support canonical pages, activation cycles, historical
  recommender participation, active/inactive state, and additional stake by
  historical recommenders.
- Support/upvote history must remain immutable and tied to the time it happened.
- Reward, visibility, and reputation formulas must not assume unlimited linear
  stake influence until caps, diminishing returns, or other anti-whale controls
  are resolved.
- The lifecycle should continue to avoid language that frames support as a
  refundable vote, passive yield, or guaranteed return.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
