# 0019: Step-Based Milestone Rewards

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's MVP tokenomics have described reward eligibility around recommendation
milestones, but the specs still left open whether rewards should be paid through
step-based milestones, continuous accrual, or a hybrid model.

The MVP needs reward timing that is easy to explain, visible in the product, and
simple enough to model before launch. Beacon also needs to avoid framing support
as a passive yield product or guaranteed return mechanism.

## Decision

For MVP, milestone rewards use a step-based model.

Rewards are only evaluated when a recommendation reaches defined supporter-count
milestones. Supporters and eligible recommenders do not continuously accrue
financial rewards between milestones, and later supporters should be shown that a
recommendation may stall below the next reward step.

This decision only resolves reward timing and mechanism shape. Exact milestone
thresholds, pool amounts, treasury percentages, eligible recommender splits,
anti-farming delays, badge policy, and final reward formulas remain unresolved
until simulation, abuse review, legal review where appropriate, and explicit
approval.

## Alternatives Considered

### Continuous rewards

- Pros: Could reduce frustration for recommendations that stall below a step.
- Cons: Harder to explain, harder to model, and more likely to sound like yield
  accrual rather than discovery participation.
- Rejected for MVP.

### Hybrid rewards

- Pros: Could combine visible milestones with partial between-step rewards.
- Cons: Adds complexity before Beacon has marketplace data and blurs the MVP
  reward story.
- Rejected for MVP.

### Step-based milestone rewards

- Pros: Simple to communicate, compatible with visible progress UI, and aligned
  with discovery-event framing.
- Cons: Recommendations may stall below the next step, leaving some supporters
  without financial rewards.
- Accepted for MVP.

## Consequences

- Product, tokenomics, API, and contract specs should model reward evaluation as
  milestone events rather than continuous accrual.
- Product UI must disclose next-step progress, eligible cohorts, and the risk
  that financial rewards are only paid if a future milestone is reached.
- Open questions should no longer ask whether MVP rewards are step-based,
  continuous, or hybrid.
- Stalled-recommendation risk remains active and should be handled with
  transparency, badges, profile reputation, and any future community-approved
  programs rather than implicit continuous reward accrual.
- Exact reward splits, formulas, thresholds, and abuse controls remain unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/product/risks.md`
- `docs/tokenomics/rewards.md`
- `docs/architecture/system-design.md`
