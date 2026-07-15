# 0018: Fixed Support Contribution

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's MVP support action lets ordinary supporters contribute a small amount of
SOL to publicly signal conviction in a recommendation. Earlier specs used `0.01
SOL` as the working support amount but left open whether the support cost should
vary by category, network conditions, or governance setting.

The MVP needs a simple, predictable support action so early users understand the
cost before confirming and so Beacon can compare support behavior across books
and series without parameter churn.

## Decision

For MVP, support/upvote is fixed at `0.01 SOL` per support action.

This fixed support amount applies to ordinary supporters. It does not change the
separate recommender stake rules for activation, reactivation, balance minimums,
top-ups, withdrawals, or locked SOL.

## Alternatives Considered

### Variable support by category

- Pros: Could tune support cost for different markets or content types.
- Cons: MVP is books-first only, and category-specific pricing adds complexity
  before Beacon has usage data.
- Rejected for MVP.

### Variable support by network conditions

- Pros: Could account for changing SOL price or transaction costs.
- Cons: Makes the core support action harder to understand and compare.
- Rejected for MVP.

### Governance-adjustable support at launch

- Pros: Lets the community tune support economics over time.
- Cons: Launch governance parameters are not mature enough for early cost churn.
- Rejected for MVP launch, but future governance may revisit support pricing.

### Fixed `0.01 SOL` support

- Pros: Simple to explain, easy to model, and produces cleaner early marketplace
  data.
- Cons: May need future adjustment if SOL price, fees, accessibility, or abuse
  patterns make the amount too high or too low.
- Accepted for MVP.

## Consequences

- Product, API, and contract specs should treat support/upvote cost as exactly
  `0.01 SOL` for MVP.
- Support confirmations must show the fixed `0.01 SOL` cost before submission.
- Open questions should no longer ask whether MVP support varies by category,
  network conditions, or governance setting.
- Future changes to support pricing require a new decision record or governance
  decision.
- Reward split formulas, milestone mechanics, anti-farming thresholds, badge
  policy, and exact recommender credit formulas remain unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
