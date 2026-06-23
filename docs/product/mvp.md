# MVP

The MVP validates Beacon as a books-first discovery marketplace.

## Objective

Test whether users will create and support book recommendations when participation requires economic commitment and creates public reputation.

## In Scope

### Books Only

The first release supports books as the only content category.

Required book metadata:

* Title
* Author
* Description or curator note
* External reference link
* Category or genre
* Creation timestamp
* Discoverer Beacon account, with wallet linking before any Solana action

Cover images and rich metadata can be added after licensing and data-source decisions are made.

### One Permanent Page Per Book

Each book should have one canonical Beacon page.

The first valid curator to create the page receives permanent discoverer credit. Later users support the existing page instead of creating fragmented duplicate markets for the same book.

### Curator Stake

A curator creates a book recommendation by locking at least `0.2 SOL` for a minimum of two weeks.

The lock acts as spam resistance and a signal of conviction. The exact stake amount is a draft parameter and may need adjustment based on SOL price, abuse patterns, and launch conditions.

### Support / Upvote

Users support a recommendation by contributing `0.01 SOL`.

Support is not a refundable vote. It represents conviction and may make the supporter eligible for milestone rewards, badge upgrades, and reputation.

### NFT Badge

Each supporter should receive an NFT badge or equivalent on-chain collectible proving participation in a specific book recommendation.

The badge represents support history, not ownership of the book or its intellectual property.

Draft badge tiers:

* Bronze when the book reaches 100 supporters.
* Silver when the book reaches 1,000 supporters.
* Gold when the book reaches 10,000 supporters.
* Diamond when the book reaches 100,000 supporters.

### Public Treasury Dashboard

The MVP should expose treasury state publicly.

At minimum:

* Community treasury balance
* Operating reserve balance
* Total SOL staked
* Available liquidity
* Lifetime recommendations
* Lifetime support transactions

### Basic Governance Eligibility

At launch, governance should be limited to wallets that have interacted with Beacon.

Initial governance can be off-chain or semi-on-chain while the rules are being validated, but the model should be designed for transparent public voting.

## Out of Scope for MVP

* Movies, games, music, or other non-book categories.
* Governance token launch.
* Complex DeFi yield strategies.
* Fully automated ranking across all content categories.
* Publisher sponsorships or affiliate revenue unless community-approved.
* Mobile apps.
* Advanced anti-Sybil identity systems.

## Success Criteria

The MVP is successful if it demonstrates:

* Users create book recommendations despite the stake requirement.
* Users support recommendations even when financial rewards are uncertain.
* NFT badges and curator profiles create non-financial motivation.
* The treasury model is understandable and publicly verifiable.
* Abuse patterns are measurable and manageable before expansion.

## Open Questions

* Should the `0.2 SOL` curator stake be fixed, dynamic, or governance-adjustable?
* Should locked curator stake yield go entirely to the treasury or be split?
* Should milestone rewards be step-based, continuous, or hybrid?
* How should duplicate books be detected and resolved?
* What metadata source should be used for book identity?
