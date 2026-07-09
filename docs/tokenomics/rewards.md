# Rewards

This document captures the draft Beacon rewards model. The numbers are working assumptions for specification and simulation, not final audited tokenomics.

## Core Actions

### Create Recommendation

A curator creates a book or series recommendation by locking at least `0.2 SOL`
for a minimum of two weeks. `0.2 SOL` is the MVP minimum, not an exact stake;
there is no maximum deposit cap on locked recommender SOL.

Recommender participant balances must be either `0 SOL` or at least `0.2 SOL`.
Later top-ups above an existing qualifying locked balance must be at least
`0.05 SOL`. These recommender stake rules do not apply to ordinary supporters who
contribute `0.01 SOL`.

The curator stake is intended to:

* Reduce spam.
* Signal conviction.
* Create a base of locked SOL that can potentially be staked.

Each canonical recommendation page has at most one active recommendation cycle. A
new user can activate or reactivate the recommendation only when the current
cycle is inactive. For MVP, an active cycle becomes eligible for inactive status
only after no recommender SOL remains locked and 90 days pass with no new
support. The original discoverer and prior reactivators are historical
recommenders and may lock additional SOL at any time to increase their share of
future upvote/support credit.

Additional stake affects future credit only. It must not rewrite past supporter
cohorts, badge history, discoverer credit, or already-earned reputation.
Partial withdrawals do not start the inactivity window while any recommender SOL
remains locked, but withdrawals must not leave a recommender balance between
`0 SOL` and `0.2 SOL`.

Extra locked SOL must not be framed as guaranteed yield, guaranteed rewards, or
uncapped influence. If additional stake affects future credit, rewards, ranking,
or visibility, it must use diminishing returns rather than linear weighting. The
exact curve and parameters remain unresolved.

### Support Recommendation

A supporter contributes `0.01 SOL` to support a book or series recommendation.

Support is non-refundable and may create eligibility for:

* Financial milestone rewards.
* NFT badge ownership and upgrades.
* Profile reputation.
* Governance participation.

## Draft Milestone Model

The initial concept uses milestone-based rewards. Later supporters do not receive immediate financial rewards unless the recommendation reaches a future milestone.

### 10 Supporters

The following milestone numbers are historical draft examples. They still require
simulation and must be updated before implementation to account for the hybrid
recommendation lifecycle and any split among eligible historical recommenders.

If 10 users support a recommendation:

* `0.05 SOL` goes to the eligible recommender share.
* `0.05 SOL` goes to treasury.

### 100 Supporters

When a recommendation reaches 100 supporters, the next pool is distributed as:

* `0.2 SOL` to the eligible recommender share.
* `0.5 SOL` split among the first 10 supporters.
* `0.25 SOL` to treasury.

Each of the first 10 supporters receives `0.05 SOL` from this milestone, equal to 5x their original support cost.

### 1,000 Supporters

When a recommendation reaches 1,000 supporters, the next pool is distributed as:

* `1 SOL` to the eligible recommender share.
* `7 SOL` split among the first 100 supporters.
* `2.25 SOL` to treasury.

Each of the first 100 supporters receives `0.07 SOL` from this milestone.

### 10,000 Supporters

When a recommendation reaches 10,000 supporters, the next pool is distributed as:

* `5 SOL` to the eligible recommender share.
* `90 SOL` split among the first 1,000 supporters.
* `7.25 SOL` to treasury.

Each of the first 1,000 supporters receives `0.09 SOL` from this milestone.

## Reward Psychology

The milestone model intentionally rewards early conviction more than late participation.

However, it creates a risk: many users may support recommendations that stall before the next reward tier. For example, supporter 10,001 may not receive financial rewards unless the recommendation reaches 100,000 supporters.

To reduce frustration, the product should make milestone progress explicit:

* Current supporters
* Next reward tier
* Progress percentage
* Eligible supporter cohort
* Expected reward pool if the milestone is reached

## NFT Badge Layer

Every supporter should receive an NFT badge or equivalent collectible for the
specific book or series recommendation.

The badge provides an immediate non-financial reward and supports the broader goal of building reputation for taste.

Draft badge evolution:

* Bronze: recommendation reaches 100 supporters.
* Silver: recommendation reaches 1,000 supporters.
* Gold: recommendation reaches 10,000 supporters.
* Diamond: recommendation reaches 100,000 supporters.

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

* One canonical page per standalone book work or recognized series.
* Discovery credit for the first valid curator.
* Single active recommendation cycles with reactivation only after inactivity.
* Extra stake rights limited to the original discoverer and prior reactivators.
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
* How should the eligible recommender share be split among the original discoverer
  and prior reactivators?
* Should later stake additions increase visibility, future support-credit share,
  both, or neither?
* What exact diminishing-returns curve, cap, or fixed staking window should apply
  to additional historical recommender stake?
* What parameters make self-farming economically unattractive?
