# 0008: Trust-Minimized Protocol Custody

## Status

Proposed

## Date

2026-06-25

## Context

Beacon's biggest trust risk is custody. If user deposits, curator locks, reward
pools, or Community Treasury funds sit in a founder wallet, company wallet, or
server-controlled account, users must trust the Beacon team not to withdraw the
funds and not to lose or expose private keys.

That trust model is weak for a Solana-native discovery marketplace. Beacon's
stronger product claim should be that users can verify how funds are held and
that the team cannot unilaterally move trust-sensitive SOL outside documented
protocol rules.

Solana programs can hold and control funds through program-controlled accounts,
including PDAs. These accounts do not have private keys. Funds move only when the
program logic permits movement.

However, upgrade authority can reintroduce trust. If a single admin can upgrade
a treasury-controlling program at any time, that admin may be able to change the
rules later. Upgrade authority, multisig configuration, governance control, and
timelocks are therefore part of Beacon's custody model.

## Decision

Beacon should design trust-sensitive economic funds around program-controlled
Solana accounts wherever feasible.

This includes:

- User support deposits before allocation.
- Curator stake principal during lock periods.
- Reward pools.
- Community Treasury balances.
- Treasury and Operating Reserve split accounting where on-chain enforcement is
  required for public trust.

Beacon should avoid ordinary externally owned wallets for user deposits and
Community Treasury custody when program-controlled accounts can enforce the
required rules.

Early-stage upgrade authority or incomplete treasury automation may remain under
team or multisig control only if it is publicly disclosed as a temporary trust
assumption. A multisig should be preferred over any single-signer authority.

The target control path is:

- Early stage: program-controlled user funds where feasible, disclosed team or
  multisig upgrade authority, and public account addresses.
- Growth stage: governance-approved treasury execution and custody-affecting
  upgrades with timelocked execution.
- Mature stage: Community Treasury execution and custody-affecting upgrades
  controlled by governance or constrained by immutable protocol rules.

Production contracts that custody meaningful SOL should be open source,
security-reviewed, and publicly documented before launch.

## Alternatives Considered

### Team-controlled custody wallet

- Pros: Simple to implement and operate early.
- Cons: Requires users to trust team honesty, private-key hygiene, and server
  security.
- Rejected as the long-term custody model for trust-sensitive funds.

### Company-controlled wallet with public dashboard only

- Pros: Improves transparency over a hidden wallet.
- Cons: Visibility does not prevent unilateral withdrawal or key compromise.
- Rejected as insufficient for Beacon's trust positioning.

### Immediate fully immutable contracts

- Pros: Minimizes upgrade authority trust.
- Cons: Risky before the protocol is validated, audited, and economically tuned;
  bugs could become impossible to patch.
- Not accepted for launch without further design and review.

### Immediate full governance control

- Pros: Strong decentralization narrative.
- Cons: Governance eligibility, quorum, timelocks, and abuse resistance are not
  fully specified; premature governance can slow critical fixes.
- Not accepted for MVP without a complete governance design.

## Consequences

- Custody status must become a first-class product and dashboard concept.
- Program IDs, treasury accounts, multisig addresses, governance authorities,
  and upgrade authorities should be publicly visible where applicable.
- The backend may index and display on-chain state, but must not become the
  custody authority for user funds.
- Upgrade authority must be documented and treated as part of the user trust
  model.
- Multisig thresholds, signer distribution, timelock duration, governance system,
  audit scope, and authority-transfer milestones remain open questions.
- Beacon must avoid claiming full decentralization while team or multisig
  authority can still affect custody-sensitive contracts.

## Related Specs

- `docs/product/treasury.md`
- `docs/product/governance.md`
- `docs/product/risks.md`
- `docs/product/mvp.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/architecture/system-design.md`
- `docs/tokenomics/staking.md`
