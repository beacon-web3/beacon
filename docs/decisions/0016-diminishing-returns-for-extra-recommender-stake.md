# 0016: Diminishing Returns For Extra Recommender Stake

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's hybrid recommendation lifecycle allows the original discoverer and prior
reactivators to add locked SOL for future upvote/support credit. ADR 0015 accepts
that eligible recommenders can lock more than the `0.2 SOL` minimum and that MVP
policy has no maximum deposit cap.

ADR 0017 specifies the balance and top-up constraints around that uncapped stake:
recommender balances must be `0 SOL` or at least `0.2 SOL`, and later top-ups
above a qualifying balance must be at least `0.05 SOL`.

Without a weighting policy, extra locked SOL could be interpreted as a linear bid
for ownership of future recommendation credit. That would weaken Beacon's
discovery and reputation positioning, create whale-dominance risk, and make the
product look too much like a passive capital game rather than a book discovery
network.

## Decision

For MVP, extra locked recommender SOL must use a diminishing-returns principle
when it affects future upvote/support credit, reward share, ranking influence, or
other future allocation mechanics.

Each additional SOL may increase future influence, but each incremental SOL must
have less marginal effect than earlier SOL. Extra stake must not be mapped
linearly to future credit, and it must not rewrite past support, badges,
discoverer credit, reactivation history, or reputation history.

This decision establishes the anti-whale weighting principle only. It does not
choose the exact curve, formula, cap, time weighting, reward split, or ranking
effect. Those parameters remain unresolved and require tokenomics simulation and
abuse review before implementation.

## Alternatives Considered

### Linear weighting by locked SOL

- Pros: Simple to calculate and explain.
- Cons: Lets large wallets dominate future credit; undermines taste and discovery
  reputation; conflicts with Beacon's goal of not becoming a pure capital race.
- Rejected for MVP.

### Hard cap only

- Pros: Easy to enforce; limits maximum influence.
- Cons: Still allows linear dominance below the cap and requires choosing an exact
  cap before simulation.
- Rejected as insufficient by itself.

### Diminishing returns

- Pros: Allows stronger conviction signaling while reducing whale dominance;
  preserves room for a later cap or time weighting; aligns with discovery-first
  positioning.
- Cons: Requires formula design, user education, and simulation before production
  implementation.
- Accepted for MVP policy.

### No effect from extra stake

- Pros: Eliminates stake-weighting risk.
- Cons: Conflicts with the accepted historical recommender stake-addition model
  and weakens conviction signaling.
- Rejected for MVP.

## Consequences

- Specs should no longer ask whether extra stake is linear versus diminishing;
  diminishing returns is accepted as the product principle.
- Backend and contract designs should store raw locked amounts but must not encode
  a linear credit formula as final policy.
- Future formula work must choose and document a diminishing-returns curve before
  extra stake affects rewards, ranking, or credit allocation in production.
- Product copy must avoid implying that more SOL linearly buys more credit,
  ownership, yield, or guaranteed rewards.
- Exact curve, cap, time weighting, reward split, and anti-farming thresholds
  remain open questions.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/tokenomics/staking.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
