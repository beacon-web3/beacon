# 0005: Treasury and Operating Reserve Split

## Status

Proposed

## Date

2026-06-21

## Context

Beacon needs a sustainable way to fund development, infrastructure, audits,
legal work, support, launch operations, and community programs without making
the product dependent only on future support activity.

The current draft model separates treasury inflows into a Community Treasury and
an Operating Reserve.

## Decision

Use a draft split where up to `20%` of treasury inflows go to an Operating
Reserve and at least `80%` remain in the Community Treasury.

This split applies to treasury inflows only. It should not take funds allocated
to curator or supporter rewards.

## Alternatives Considered

### No operating reserve

- Pros: Maximizes community treasury balance.
- Cons: Leaves development, operations, legal, and audit funding unclear.
- Rejected as unsustainable.

### Higher operating reserve

- Pros: More reliable funding for team execution.
- Cons: Higher trust burden and weaker community-treasury narrative.
- Not accepted without stronger justification.

### Lower operating reserve

- Pros: More conservative and community-favorable.
- Cons: May underfund early execution.
- Possible future phase-down option.

## Consequences

- The split remains draft until explicitly confirmed and reviewed.
- Public treasury dashboards should show Community Treasury and Operating
  Reserve separately.
- Governance may later adjust future percentages after a milestone or fixed
  bootstrap period.

## Related Specs

- `docs/product/treasury.md`
- `docs/product/governance.md`
- `docs/tokenomics/rewards.md`
- `docs/product/assumptions.md`
