# 0006: Conservative Native SOL Staking Preference

## Status

Proposed

## Date

2026-06-21

## Context

Beacon may hold SOL in treasury accounts and locked recommender stakes. These
funds could potentially be staked while preserving liquidity and principal
accounting.

DeFi yield strategies may create additional smart-contract, liquidity, custody,
and perception risks.

## Decision

Prefer conservative native SOL staking assumptions over DeFi yield strategies
unless a different model is explicitly requested, reviewed, and approved.

Staking yield should be framed as treasury management, not user-facing passive
yield.

## Alternatives Considered

### DeFi yield farming

- Pros: Potentially higher yield.
- Cons: Higher risk, more complexity, and worse product-positioning risk.
- Rejected for default assumptions.

### No staking

- Pros: Simpler and lowest staking risk.
- Cons: Leaves potential treasury-supporting yield unused.
- Still possible if risk review rejects staking.

## Consequences

- Contract and backend design should preserve clean principal accounting.
- Locked recommender stake principal must remain reclaimable according to the lock
  rules if staking is used.
- Any staking implementation requires security and legal review before launch.

## Related Specs

- `docs/tokenomics/staking.md`
- `docs/product/treasury.md`
- `docs/product/risks.md`
- `docs/product/assumptions.md`
