# Rewards

This document captures the draft Beacon rewards model. The numbers are working assumptions for specification and simulation, not final audited tokenomics.

## Core Actions

### Create Recommendation

A curator creates a book recommendation by locking at least `0.2 SOL` for a minimum of two weeks.

The curator stake is intended to:

* Reduce spam.
* Signal conviction.
* Create a base of locked SOL that can potentially be staked.

### Support Recommendation

A supporter contributes `0.01 SOL` to support a book recommendation.

Support is non-refundable and may create eligibility for:

* Financial milestone rewards.
* NFT badge ownership and upgrades.
* Profile reputation.
* Governance participation.

## Draft Milestone Model

The initial concept uses milestone-based rewards. Later supporters do not receive immediate financial rewards unless the recommendation reaches a future milestone.

### 10 Supporters

If 10 users support a book:

* `0.05 SOL` goes to the original curator.
* `0.05 SOL` goes to treasury.

### 100 Supporters

When a book reaches 100 supporters, the next pool is distributed as:

* `0.2 SOL` to the original curator.
* `0.5 SOL` split among the first 10 supporters.
* `0.25 SOL` to treasury.

Each of the first 10 supporters receives `0.05 SOL` from this milestone, equal to 5x their original support cost.

### 1,000 Supporters

When a book reaches 1,000 supporters, the next pool is distributed as:

* `1 SOL` to the original curator.
* `7 SOL` split among the first 100 supporters.
* `2.25 SOL` to treasury.

Each of the first 100 supporters receives `0.07 SOL` from this milestone.

### 10,000 Supporters

When a book reaches 10,000 supporters, the next pool is distributed as:

* `5 SOL` to the original curator.
* `90 SOL` split among the first 1,000 supporters.
* `7.25 SOL` to treasury.

Each of the first 1,000 supporters receives `0.09 SOL` from this milestone.

## Reward Psychology

The milestone model intentionally rewards early conviction more than late participation.

However, it creates a risk: many users may support recommendations that stall before the next reward tier. For example, voter 10,001 may not receive financial rewards unless the book reaches 100,000 supporters.

To reduce frustration, the product should make milestone progress explicit:

* Current supporters
* Next reward tier
* Progress percentage
* Eligible supporter cohort
* Expected reward pool if the milestone is reached

## NFT Badge Layer

Every supporter should receive an NFT badge or equivalent collectible for the specific book recommendation.

The badge provides an immediate non-financial reward and supports the broader goal of building reputation for taste.

Draft badge evolution:

* Bronze: book reaches 100 supporters.
* Silver: book reaches 1,000 supporters.
* Gold: book reaches 10,000 supporters.
* Diamond: book reaches 100,000 supporters.

Badges should not represent ownership of book IP.

## Treasury Split

Treasury inflows from support activity should be split into:

* Community Treasury: draft `80%` of treasury inflows.
* Operating Reserve: draft `20%` of treasury inflows.

The Operating Reserve funds Beacon team operations such as development, infrastructure, audits, support, and launch work.

This split should be transparent before launch and should not be renegotiated constantly. A future governance milestone may allow the community to vote on changing future allocations.

## Known Risks

### Self-Farming

Attackers may create a recommendation and support it from many wallets to capture curator and early supporter rewards.

Mitigations to evaluate:

* Keep treasury retention high enough to make farming unattractive.
* Delay rewards.
* Keep locked capital at risk for enough time.
* Use wallet age, transaction history, and balance only as weak signals, not primary protection.
* Monitor suspicious clusters off-chain before automating enforcement.

### Popularity Bias

Famous books may attract more support than genuinely under-discovered books.

Mitigations to evaluate:

* One canonical page per book.
* Discovery credit for the first valid curator.
* Ranking formulas that include freshness, category, velocity, and early conviction.

### Ponzi Perception

Rewards are funded partly by later supporters, which may create a harmful perception if the product is framed as a way to earn yield.

Beacon should be framed as reputation-based discovery, with rewards as a bonus mechanism.

### Stalled Recommendations

Recommendations may stall below the next milestone, leaving supporters with no financial reward.

Mitigations to evaluate:

* NFT badge value and profile reputation.
* Visible milestone progress.
* Continuous or hybrid reward pools.
* Periodic rewards funded by staking yield or community-approved treasury programs.

## Open Questions

* Should rewards remain milestone-based or become continuous?
* What exact percentage should stay in treasury at each milestone?
* Should the original curator receive permanent future participation in rewards?
* Should later stake additions increase visibility without changing discoverer credit?
* What parameters make self-farming economically unattractive?
