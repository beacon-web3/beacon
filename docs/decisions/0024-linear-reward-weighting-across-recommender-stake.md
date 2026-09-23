# 0024: Linear Reward Weighting Across Recommender Stake

## Status

Accepted

Supersedes `0016-diminishing-returns-for-extra-recommender-stake.md`.

## Date

2026-09-23

## Context

Beacon's hybrid recommendation lifecycle allows the original discoverer and
prior reactivators (the historical recommender set) to hold locked SOL on the
same recommendation while an active recommendation cycle is running. ADR 0011
accepts this model, ADR 0015 accepts the `0.2 SOL` minimum with no deposit cap,
and ADR 0017 constrains balances to `0 SOL` or at least `0.2 SOL` with `0.05
SOL` minimum top-ups.

ADR 0016 accepted a diminishing-returns principle for extra locked SOL to limit
whale dominance. That principle was adopted because a linear reading made extra
stake look like a direct ownership bid on future credit. After working through
the lifecycle, the reward weighting between the active recommender and the
historical recommender set needs a simpler, explainable rule: each recommender's
share of an active recommendation's future reward credit is proportional to
their locked SOL among all recommenders holding stake on that recommendation.

Linear weighting is explicitly chosen for MVP reward math because it makes
reward distribution across the active recommender and historical recommenders
straightforward to compute and to explain. Risk controls shift from the
weighting curve to balance minimums, support contribution rules, milestone
design, and abuse monitoring.

## Decision

For MVP, future upvote/support credit and reward share on an active
recommendation is distributed linearly in proportion to each recommender's
locked SOL relative to the total locked recommender SOL currently held on that
recommendation by the active recommender and historical recommenders.

Each recommender share satisfies:

```text
share = locked SOL of recommender / total locked SOL of all recommenders on the recommendation
```

This applies among all recommenders holding stake on the recommendation,
including:

- The current active recommender.
- Historical recommenders (original discoverer and prior reactivators) who have
  re-staked while the cycle is active.

When a historical recommender reactivates a deactivated recommendation, they
become the active recommender again while remaining part of the historical
recommender set. Their locked SOL counts toward the same linear share as the
active recommender.

Extra locked SOL still affects future credit allocation only. It must not
rewrite past support credit, badges, discoverer credit, or reputation history.

This decision establishes the weighting principle only. It does not choose the
exact milestone thresholds, reward pool sizes, treasury splits, tiers, or
anti-farming parameters. Those remain draft assumptions pending tokenomics
simulation and abuse review.

## Alternatives Considered

### Diminishing returns (0016)

- Pros: Reduces whale dominance from extra stake; aligned with discovery-first
  positioning.
- Cons: Requires an exact curve, complicates reward math across multiple
  recommenders, and is harder to explain to users. It was never parameterized.
- Superseded for MVP in favor of linear weighting.

### Fixed split among recommenders regardless of stake

- Pros: Simplest formula; no stake weighting at all.
- Cons: Removes the conviction-signaling value of additional locked SOL and
  conflicts with the accepted historical recommender stake-addition model.
- Rejected for MVP.

### Linear weighting by locked SOL share

- Pros: Simple, explainable reward math; each SOL counts equally; easy to
  compute across the active recommender and historical recommender set.
- Cons: Lets larger recommender balances earn proportionally more future credit;
  requires balance minimums, support rules, milestone design, and abuse
  monitoring to contain whale-dominance risk.
- Accepted for MVP.

### Time-weighted or cap-based weighting

- Pros: Could reward early recommender commitment and bound maximum influence.
- Cons: Adds formula complexity before Beacon has enough marketplace data.
- Rejected for MVP; may be revisited by future governance.

## Consequences

- Reward and credit-share specs should describe linear proportional weighting by
  locked SOL across the active recommender and historical recommenders.
- Docs that previously referenced diminishing returns for extra recommender
  stake are superseded by this decision.
- Backend and contract designs should store raw locked amounts per recommender
  participant so linear shares can be computed; they must not encode a
  non-linear curve.
- Anti-whale and anti-farming controls remain necessary through balance
  minimums (`0 SOL` or at least `0.2 SOL`, `0.05 SOL` minimum top-ups), fixed
  support contributions, milestone design, and abuse monitoring.
- Exact milestone numbers, reward pool sizes, splits, tiers, and anti-farming
  thresholds remain open questions pending simulation and review.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/decisions/0011-hybrid-recommendation-lifecycle.md`
- `docs/decisions/0013-recommendation-inactivity-window.md`
- `docs/decisions/0015-minimum-recommender-stake-no-deposit-cap.md`
- `docs/decisions/0017-recommender-stake-balance-and-top-up-minimums.md`
- `plans/completed/0016-recommendation-lifecycle-data-model.md`