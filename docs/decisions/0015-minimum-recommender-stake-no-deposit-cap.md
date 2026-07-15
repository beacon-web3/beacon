# 0015: Minimum Recommender Stake With No Deposit Cap

## Status

Accepted

## Date

2026-07-09

## Context

Beacon uses locked recommender SOL as spam resistance and as a signal of
conviction for activating or reactivating a book or series recommendation.
Earlier specs treated `0.2 SOL` as the required base stake but left open whether
that amount was fixed, dynamic, governance-adjustable, or capped.

The MVP needs a simple stake rule that is easy to explain before implementing
creation, reactivation, withdrawal, and inactive-cycle logic. At the same time,
Beacon should not imply that higher locked SOL guarantees higher returns or
uncapped reward influence.

## Decision

For MVP, `0.2 SOL` is the minimum locked recommender stake required to activate
or reactivate a recommendation page.

There is no maximum deposit cap on recommender SOL locked into an eligible
recommendation by an eligible recommender. A recommender may lock more than `0.2
SOL` initially or later add more locked SOL if they are the original discoverer
or a prior reactivator for that page.

This decision only resolves the minimum stake and deposit-cap rule. ADR 0016
resolves that extra locked SOL must follow a diminishing-returns principle if it
affects future upvote/support credit, reward splits, ranking, or visibility.
Product copy must avoid implying that extra locked SOL creates guaranteed yield,
guaranteed rewards, or uncapped influence.

ADR 0017 specifies that recommender locked balances must be either `0 SOL` or at
least `0.2 SOL`, and later top-ups above an existing qualifying balance must be at
least `0.05 SOL`.

## Alternatives Considered

### Fixed exact `0.2 SOL` stake

- Pros: Simplest to explain; limits capital concentration.
- Cons: Prevents stronger conviction signaling and later historical recommender
  stake additions already accepted in the hybrid lifecycle.
- Rejected for MVP.

### Dynamic minimum stake

- Pros: Could adapt to SOL price, abuse patterns, or category-specific economics.
- Cons: Adds policy complexity before Beacon has enough marketplace data.
- Rejected for MVP.

### Governance-adjustable minimum at launch

- Pros: Lets the community tune economics over time.
- Cons: Beacon has no mature launch governance process yet, and early parameter
  churn would make MVP behavior harder to understand.
- Rejected for MVP launch, but future governance may revisit parameters.

### Minimum stake with no deposit cap

- Pros: Keeps a clear spam-resistance floor while allowing stronger conviction
  signals and additional historical recommender stake.
- Cons: Requires an exact diminishing-returns formula before extra stake can
  safely affect rewards or ranking.
- Accepted for MVP deposit rules.

## Consequences

- Creation and reactivation flows must enforce at least `0.2 SOL` locked.
- Eligible recommenders may lock more than the minimum; there is no hard maximum
  deposit cap in the MVP product policy.
- Backend and contract designs should store actual locked amounts rather than a
  boolean base-stake flag.
- Backend, contract, and withdrawal flows must avoid recommender dust balances
  below `0.2 SOL` per ADR 0017.
- Withdrawal flows must continue to distinguish partial withdrawals from full
  withdrawals for inactivity eligibility.
- Open questions should no longer ask whether `0.2 SOL` is fixed, dynamic, or
  governance-adjustable for MVP.
- Exact diminishing-returns curve, reward splits, ranking influence, and
  anti-whale parameters remain unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
