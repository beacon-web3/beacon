# Open Questions

This file centralizes unresolved Beacon product, economic, governance,
architecture, legal, and launch questions so agents do not invent policy during
implementation.

## Product

- What exact duplicate-risk scoring and matching algorithm should Beacon use
  before immediate canonical page creation?
- What manual review service level is acceptable for duplicate-risk candidate
  pages?
- What book metadata source should Beacon use for author data, categories,
  external links, enrichment, and optional cover images?
- Should curator notes have length, moderation, or quality requirements?
- Should inactive recommendations require moderation review before reactivation?
- What profile signals best represent curator reputation without turning Beacon
  into a pure financial leaderboard?

## Tokenomics

- Should the `0.2 SOL` curator stake be fixed, dynamic, or governance-adjustable?
- Should support remain fixed at `0.01 SOL`, or should it vary by category,
  network conditions, or governance setting?
- Should milestone rewards be step-based, continuous, or hybrid?
- How should future upvote/support credit be split among the original discoverer
  and prior reactivators?
- Should historical recommender stake additions be linear, capped, time-weighted,
  or subject to diminishing returns?
- What minimum additional stake should be required when a historical recommender
  increases future credit share?
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
- Which MVP balances must be program-controlled before launch, and which can
  temporarily remain under disclosed multisig or manual administration?
- Which Solana multisig or governance system should control early treasury and
  upgrade authorities?
- What multisig threshold and signer distribution are acceptable for early
  authority control?
- What timelock duration should apply before high-impact treasury spending or
  protocol changes execute?

## Governance

- What exact wallet actions make a user governance-eligible?
- Should voting weight be one-wallet-one-vote, badge-weighted, reputation-based,
  stake-weighted, or hybrid?
- Which decision categories require a supermajority?
- Should early governance be off-chain, on-chain, or hybrid?
- Which custody-affecting changes require governance approval?
- When should Beacon transfer program upgrade authority from team or multisig
  control to governance control?
- What process lets users inspect and react to timelocked upgrades before
  execution?

## Legal And Trust

- What language is required to avoid investment-return or guaranteed-profit
  claims?
- What jurisdictions should be reviewed before public launch?
- What disclosures are required for affiliate revenue, sponsored placement, or
  featured auctions?
- What moderation policy is needed for book metadata, descriptions, and links?
- What custody disclosures are required if any early-stage funds or authorities
  remain under team or multisig control?
- Which smart contracts must receive professional security review before public
  launch?
- What public audit report, source-code, and known-risk disclosures are required
  before contracts custody meaningful SOL?

## Architecture

- Which data belongs on-chain versus off-chain for the MVP?
- How should the backend index Solana events and reconcile failed or delayed
  transactions?
- Should Solana event monitoring for the production-like MVP run in Django, a
  separate worker or indexer, scheduled jobs, or direct Nuxt client RPC reads?
- What API boundaries should exist between `apps/web`, `apps/api`,
  `apps/contracts`, and `packages/sdk`?
- What observability is required for treasury, support, reward, and staking
  flows?
- How should Solana PDAs and program-controlled accounts be structured for user
  deposits, curator locks, reward pools, Community Treasury funds, and Operating
  Reserve split accounting?
- How should backend indexing prove that displayed treasury balances match
  on-chain account state?
- How should program upgrade authority be represented in the frontend and
  treasury dashboard?

## Infrastructure And Launch

- Should the first production-like Django deployment use Render free tier or
  Google Cloud Run free tier?
- Should the first managed PostgreSQL provider be Neon or Aiven?
- What cold-start delay is acceptable for early MVP testing before paid or
  always-on backend hosting is required?
- Which uptime, backup, and data-retention thresholds must be met before public
  beta?
