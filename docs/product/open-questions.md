# Open Questions

This file centralizes unresolved Beacon product, economic, governance,
architecture, legal, and launch questions so agents do not invent policy during
implementation.

## Product

- How should duplicate books be detected and resolved before a canonical page is
  created?
- What book metadata source should Beacon use for identity, author data,
  categories, external links, and optional cover images?
- Should curator notes have length, moderation, or quality requirements?
- What profile signals best represent curator reputation without turning Beacon
  into a pure financial leaderboard?

## Tokenomics

- Should the `0.2 SOL` curator stake be fixed, dynamic, or governance-adjustable?
- Should support remain fixed at `0.01 SOL`, or should it vary by category,
  network conditions, or governance setting?
- Should milestone rewards be step-based, continuous, or hybrid?
- How should rewards behave when a recommendation stalls below the next
  milestone?
- What anti-farming thresholds or delays should apply before rewards are paid?

## Badges And Reputation

- Should badges be minted immediately on support, upgraded dynamically at
  milestones, or represented by metadata updates?
- Should badge transfers be allowed, restricted, or discouraged?
- How should badge metadata avoid use of copyrighted cover art or protected book
  IP?

## Treasury And Staking

- Should locked curator stake yield go entirely to the treasury, the curator, or
  a split between both?
- What minimum liquidity should the treasury keep unstaked?
- Which staking providers or validators are acceptable, and how should validator
  risk be communicated?
- When can governance adjust the Operating Reserve percentage?

## Governance

- What exact wallet actions make a user governance-eligible?
- Should voting weight be one-wallet-one-vote, badge-weighted, reputation-based,
  stake-weighted, or hybrid?
- Which decision categories require a supermajority?
- Should early governance be off-chain, on-chain, or hybrid?

## Legal And Trust

- What language is required to avoid investment-return or guaranteed-profit
  claims?
- What jurisdictions should be reviewed before public launch?
- What disclosures are required for affiliate revenue, sponsored placement, or
  featured auctions?
- What moderation policy is needed for book metadata, descriptions, and links?

## Architecture

- Which data belongs on-chain versus off-chain for the MVP?
- How should the backend index Solana events and reconcile failed or delayed
  transactions?
- What API boundaries should exist between `apps/web`, `apps/api`,
  `apps/contracts`, and `packages/sdk`?
- What observability is required for treasury, support, reward, and staking
  flows?
