# 0017: Recommender Stake Balance And Top-Up Minimums

## Status

Accepted

## Date

2026-07-09

## Context

ADR 0015 accepts `0.2 SOL` as the minimum locked recommender stake for activating
or reactivating a recommendation, with no maximum deposit cap. ADR 0016 accepts
diminishing returns for any extra locked-SOL influence.

The remaining implementation question is how small locked balances and later
top-ups should behave. If a recommender can leave dust balances below the
activation minimum, the product has to explain whether that participant still
counts as locked, whether the inactivity window starts, and whether tiny balance
changes can be used to spam the system.

This decision applies only to recommender participants with locked SOL. It does
not apply to ordinary supporters who contribute `0.01 SOL` to support a
recommendation.

## Decision

For MVP, a recommender participant's locked SOL balance on a recommendation must
be either exactly `0 SOL` or at least `0.2 SOL`.

Activation and reactivation require locking at least `0.2 SOL`. After that, a
recommender may lock more SOL without a maximum deposit cap. Later top-ups above
an existing qualifying balance must be at least `0.05 SOL` per increase.

Withdrawals must not leave a recommender participant with a locked balance above
`0 SOL` but below `0.2 SOL`. A withdrawal that would reduce the balance below
`0.2 SOL` must either be rejected or treated as a full withdrawal to `0 SOL`,
with the existing warning that a full withdrawal can start the inactivity-window
conditions if no recommender SOL remains locked on the active cycle.

## Alternatives Considered

### Allow any positive locked balance

- Pros: Maximum flexibility for users.
- Cons: Creates dust balances, confusing inactivity semantics, and more edge
  cases for contracts, APIs, and UI.
- Rejected for MVP.

### Require every top-up to be at least `0.2 SOL`

- Pros: Very simple and consistent with the activation minimum.
- Cons: Too restrictive for recommenders who already maintain a qualifying locked
  balance and want to add smaller conviction signals over time.
- Rejected for MVP.

### Use `0 SOL` or at least `0.2 SOL`, with `0.05 SOL` minimum top-ups

- Pros: Prevents dust balances, keeps activation/reactivation meaningful, and
  allows modest later stake increases without excessive friction.
- Cons: Adds one more validation rule to stake-addition and withdrawal flows.
- Accepted for MVP.

## Consequences

- Backend and contract validation must enforce recommender locked balances of
  `0 SOL` or at least `0.2 SOL`.
- Stake-increase flows must enforce a `0.05 SOL` minimum top-up for recommenders
  who already have at least `0.2 SOL` locked.
- Withdrawal flows must prevent or convert withdrawals that would leave a balance
  between `0 SOL` and `0.2 SOL`.
- Full-withdrawal warnings remain required because full withdrawal can contribute
  to inactive eligibility.
- Ordinary supporters contributing `0.01 SOL` are unaffected by this rule.
- Exact diminishing-returns curve, reward split, ranking effect, and cap policy
  remain unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
