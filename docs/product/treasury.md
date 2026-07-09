# Treasury

Beacon's treasury model should be public, understandable, and separated from team operating funds.

## Treasury Goals

The treasury exists to:

* Fund rewards and ecosystem programs.
* Support platform growth.
* Create long-term resilience if user growth slows.
* Build trust through public verification.
* Make monetization and spending visible to participants.

## Treasury Sources

Potential sources:

* Treasury share from support activity.
* Yield from staked treasury SOL.
* Yield from locked recommender stake SOL.
* Community-approved affiliate revenue.
* Community-approved sponsored placements.
* Community-approved premium analytics or business tools.

New revenue sources should require governance approval before activation.

## Draft Split

The current draft split for treasury inflows is:

* `80%` to Community Treasury.
* `20%` to Operating Reserve.

This applies to funds that enter the treasury after user rewards are calculated. It does not take from amounts already allocated to curators or supporter rewards.

## Community Treasury

The Community Treasury should fund ecosystem-level uses approved through governance.

Examples:

* Curator competitions.
* Discovery grants.
* Reading challenges.
* Marketing campaigns.
* Community awards.
* Public-good tooling.

Community Treasury funds should ultimately be held in Solana program-controlled
accounts and released only through documented protocol or governance rules. The
long-term trust goal is that Beacon contributors cannot unilaterally move
community funds by signing from a founder, company, or server-controlled wallet.

## Operating Reserve

The Operating Reserve funds the Beacon team and core operating needs.

Examples:

* Product development.
* Infrastructure.
* Security audits.
* Legal and compliance review.
* Support operations.
* Design and content work.

The Operating Reserve should be public, but not subject to constant short-term renegotiation. Builders need predictable funding to maintain the platform.

Any Operating Reserve funds controlled by humans before full governance
automation should use disclosed controls, preferably a multisig rather than a
single signer. User-facing reporting must distinguish Operating Reserve custody
from program-controlled user deposits, curator locks, reward pools, and
Community Treasury balances.

## Trust-Minimized Custody Direction

Beacon's trust model should move from "trust the team" toward "verify the
rules." Users should not have to trust that developers will avoid withdrawing or
losing pooled SOL when that SOL is intended to be locked, rewarded, or governed
by the protocol.

For trust-sensitive funds, the preferred Solana design is:

* User deposits flow into program-controlled accounts, such as PDAs.
* No person, company, backend service, or founder wallet has a private key for
  those accounts.
* Funds move only when Beacon's Solana program rules permit movement.
* Curator stake principal can be released only under documented lock rules.
* Reward pools and Community Treasury funds can be released only under documented
  reward, split, or governance rules.

Beacon should avoid custody patterns where user deposits or community funds sit
in ordinary externally owned wallets controlled by a person or server key. If a
manual control remains during an early phase, it must be disclosed as a temporary
trust assumption, protected by multisig where possible, and tracked as a launch
risk.

## Control Phases

Beacon may need staged decentralization so the protocol can launch safely without
pretending to be more decentralized than it is.

### Early Stage

* Program-controlled accounts should be used for user deposits, curator locks,
  reward pools, and other trust-sensitive economic balances wherever feasible.
* Upgrade authority and incomplete treasury automation may remain under team
  control, but should be publicly disclosed.
* Any human-controlled authority should prefer multisig over a single signer.
* Contract source, account addresses, and authority addresses should be public.

### Growth Stage

* Upgrade authority and treasury execution should move toward governance or
  governance-approved multisig control.
* Timelocks should be introduced before high-impact treasury or protocol changes
  can execute.
* Public proposals should describe the amount, recipient, authority path, and
  expected impact before funds move.

### Mature Stage

* Community Treasury execution should be fully governed or constrained by
  governance-approved smart contract rules.
* Unilateral founder or team withdrawal of Community Treasury funds should be
  impossible.
* Protocol upgrades that can affect custody, balances, splits, rewards, or user
  rights should require governance approval and a waiting period.

## Possible Future Phase-Down

The white paper may define a staged operating reserve policy.

Example:

* Bootstrap phase: 20% to Operating Reserve.
* Growth phase: 15% to Operating Reserve.
* Mature phase: 10% to Operating Reserve.

Alternatively, the initial 20% can remain fixed until a milestone, after which the community may vote on future changes.

Potential milestone examples:

* 50,000 active users.
* 1,000,000 support transactions.
* A defined date after launch.
* A treasury balance threshold.

## Public Dashboard Requirements

The treasury dashboard should show:

* Community Treasury balance.
* Operating Reserve balance.
* Total SOL staked.
* Available liquidity.
* Lifetime support inflows.
* Lifetime rewards paid.
* Lifetime staking yield.
* Recent treasury transactions.
* Active governance-approved spending programs.
* Custody/control status for major balances, such as program-controlled,
  multisig-controlled, governance-controlled, or manually administered.
* Program IDs, treasury account addresses, multisig addresses, upgrade authority
  addresses, and governance authority addresses where applicable.

## Trust Requirements

* Treasury wallets should be public.
* Treasury accounting should be easy to verify.
* Sponsored or affiliate revenue should be labeled.
* Community funds and operating funds should not be mixed in user-facing reporting.
* Any treasury spending proposal should include purpose, amount, expected impact, and recipient.
* User deposits, curator lock principal, reward pools, and Community Treasury
  balances should be program-controlled wherever feasible.
* Any admin, multisig, governance, or upgrade authority capable of affecting
  treasury funds should be public and explained.
* Upgrade authority should be treated as part of the custody model because an
  unrestricted upgrade can change fund movement rules.
* Production contracts that custody meaningful SOL should be open source and
  security-reviewed before public launch.

## Open Questions

* Should Operating Reserve funds be controlled by a multisig?
* Who signs Community Treasury transactions before full governance automation?
* What liquidity buffer is required for rewards and unlocks?
* Which dashboard values must come directly from chain data?
* How often should treasury reports be published?
* Which Solana multisig or governance system should control early treasury and
  upgrade authorities?
* What timelock duration is required before high-impact treasury or protocol
  changes execute?
* What milestone should trigger transfer of upgrade authority from team control
  to governance control?
