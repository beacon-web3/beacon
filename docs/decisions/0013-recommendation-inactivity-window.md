# 0013: Recommendation Inactivity Window

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's hybrid recommendation lifecycle allows a canonical standalone book work
or recognized series page to move from an active recommendation cycle to an
inactive state, after which an eligible new recommender can reactivate it by
locking at least the required `0.2 SOL` minimum.

The MVP needs a concrete inactivity window before backend models, scheduled
checks, API states, and user-facing reactivation copy can be implemented. That
window should only begin after the active recommender has no locked SOL remaining
on the recommendation. Because early MVP discovery and recommender competition
are expected to be low, the window should avoid premature deactivation while
still allowing stale recommendations to be revived.

## Decision

For MVP, an active recommendation cycle becomes eligible for inactive status only
after both conditions are true:

- No recommender SOL remains locked on the active cycle.
- The cycle has `90 days` with no new support.

Partial withdrawals do not start the inactivity window. For example, if a
recommender initially locks `1 SOL`, withdrawing `0.8 SOL` does not start the
inactivity window because the required base stake, currently `0.2 SOL`, remains
locked. The window can start only after the recommender withdraws all remaining
locked SOL.

The no-support window is measured from the later of the time when no recommender
SOL remains locked on the active cycle or the latest valid support transaction on
that cycle. Reactivation remains unavailable to new users until the page is
inactive.

The UI must warn a recommender before a withdrawal that would leave no SOL locked
on the active cycle, because that action can start the inactivity window if no
new support arrives.

This decision only resolves the inactivity trigger and duration. It does not
resolve reward split formulas across historical recommenders.
`0014-reactivation-moderation-policy.md` resolves the default reactivation
moderation rule. `0015-minimum-recommender-stake-no-deposit-cap.md` resolves the
MVP activation and reactivation minimum stake.

## Alternatives Considered

### 30 days with no new support

- Pros: Faster rotation and more opportunities for new recommenders.
- Cons: Too aggressive for an MVP with low early discovery volume; could make
  valid recommendations appear stale before enough users have seen them.
- Rejected for MVP.

### 60 days with no new support

- Pros: Middle ground between freshness and stability.
- Cons: Still may be short while Beacon has limited traffic and category depth.
- Rejected for MVP in favor of a more conservative window.

### 90 days with no new support after no recommender SOL remains locked

- Pros: Gives recommendations a meaningful discovery runway during low-traffic MVP
  conditions; simple to explain and implement; prevents partial withdrawals from
  prematurely opening a page for reactivation.
- Cons: Slower reactivation opportunities if a recommendation is genuinely stale.
- Accepted for MVP.

### Dynamic inactivity scoring

- Pros: Could account for category velocity, page age, supporter cohorts, and
  seasonal behavior.
- Cons: Adds complexity and hidden policy before Beacon has enough data.
- Rejected for MVP.

## Consequences

- Product copy can explain inactivity as zero locked recommender SOL plus `90
  days with no new support`.
- Backend lifecycle logic should store enough timestamps and locked stake state to
  determine when an active cycle reaches zero locked recommender SOL and the
  latest valid support transaction per active cycle.
- Withdrawal flows must distinguish partial withdrawals from full withdrawals and
  warn users before a withdrawal that leaves no SOL locked.
- Scheduled jobs or admin workflows can mark eligible cycles inactive, but the
  exact automation mechanism remains an implementation detail.
- Product and tokenomics docs should no longer list the inactivity duration as an
  unresolved question.
- Historical recommender credit formulas and anti-whale controls remain
  unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
