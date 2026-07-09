# Staking

This document captures the draft staking model for Beacon-held SOL.

## Stakable Pools

Beacon may have two main SOL pools:

* Treasury funds accumulated from support activity.
* Locked recommender stakes held for active recommendation cycles and historical
  recommender stake additions.

Both pools can create staking yield, but they have different user expectations and risk constraints.

## Treasury Staking

Treasury SOL is the clearest candidate for staking.

Potential uses of staking yield:

* Fund platform operations.
* Add to community reward pools.
* Fund curator grants or competitions.
* Build launch and marketing budgets.
* Strengthen long-term treasury sustainability.

Treasury staking should be publicly visible in the treasury dashboard.

## Locked Recommender Stake Staking

Recommender stakes are locked for at least the required minimum period. During
the lock period, Beacon may stake this SOL if the mechanism preserves the user's
ability to reclaim the principal when the lock ends.

The recommender should not experience additional withdrawal uncertainty because
their stake was staked by the protocol.

Locked recommender stake principal should remain under program-controlled rules, not
under a founder, company, or backend-controlled wallet. If staking is introduced,
the staking path must not create an alternate authority that can redirect or
withdraw user principal outside the documented lock and release rules.

For the recommendation lifecycle, the original discoverer and prior reactivators
may add locked SOL to increase future upvote/support credit share. That extra
stake must not change historical credit or create a user-facing yield product.

## Yield Allocation Options

### Option 1: All Yield to Treasury

The curator receives the original stake back after the lock period. All staking yield flows to the treasury.

Advantages:

* Simple.
* Builds treasury faster.
* Easy to explain.

Tradeoff:

* Recommenders receive no direct yield from their locked capital.

### Option 2: Split Yield

Part of the yield goes to the curator and part goes to treasury.

Advantages:

* Makes creating or reactivating recommendations slightly more attractive.
* Feels fair to users whose locked capital generated yield.

Tradeoff:

* More accounting complexity.

### Option 3: Yield Funds Curator Rewards

Yield from locked stakes and treasury funds goes into community reward programs.

Advantages:

* Reinforces the discovery ecosystem.
* Can reward quality and influence beyond raw support counts.
* Helps recommendations that stall below milestone thresholds.

Tradeoff:

* Requires governance and clear program rules.

## Preferred Initial Direction

For the MVP, Beacon should prefer conservative native SOL staking and avoid complex DeFi yield strategies.

Native staking is easier for users to understand and has a clearer risk profile. DeFi yield farming introduces smart contract risk, liquidity risk, protocol risk, and reputational risk that are not necessary for validating the discovery marketplace.

Any staking implementation must preserve clear custody boundaries. Treasury
staking, recommender stake staking, and reward-pool liquidity should be visibly
separated in accounting and should not rely on undisclosed private-key control
over user principal.

## Product Framing

Staking should be framed as treasury management, not as a user-facing yield product.

Users should understand Beacon as:

> A platform for backing and discovering valuable content.

Not:

> A platform for depositing SOL to earn yield.

## Transparency Requirements

The product should show:

* Total SOL in treasury.
* Total SOL staked.
* Available liquidity.
* Yield earned over time.
* Allocation of yield between community treasury, operating reserve, and reward programs.

## Risks

* Staked SOL may not be instantly liquid.
* Validator performance can affect yield.
* Slashing and protocol-level risks must be understood for the chosen staking approach.
* Users may misunderstand staking as a yield guarantee or as a way to buy past
  reputation.
* Treasury loss would damage platform trust.
* Staking integrations may introduce new authority paths that weaken the
  program-controlled custody model.

## Open Questions

* Who receives yield from locked recommender stakes?
* What liquidity buffer is required for unlocks and rewards?
* Which validators or staking providers are acceptable?
* Which staking decisions require governance approval?
* What staking risk disclosures are required before launch?
* How can native staking be implemented while preserving program-controlled
  custody and timely recommender stake withdrawal?
* Should extra historical recommender stake have caps, diminishing returns, or
  fixed staking windows?
* Which staking authority addresses must be visible in the treasury dashboard?
