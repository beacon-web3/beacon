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

### One Permanent Page Per Book Work Or Series

Each standalone book work or recognized book series should have one canonical
Beacon page. Beacon should not create separate MVP pages for editions, ISBNs,
translations, box sets, or individual volumes inside a recognized series.

For MVP, a recognized series is represented only by the series-level canonical
page. Individual-volume pages can be reconsidered later only through an explicit
product or governance decision.

The first valid curator to create the page receives permanent historical
discoverer credit. Later activity happens on the same page instead of creating
fragmented duplicate markets for the same work or series.

Users create a candidate page by entering a title and author or authors. Beacon
must run a high-sensitivity duplicate-risk check before immediate creation. If
duplicate risk is low, the canonical page can be created immediately and users can
later report duplicates. If duplicate risk is detected, Beacon must show likely
duplicate pages and warn the creator before they continue.

If the creator proceeds after seeing duplicate risk, the candidate page requires
manual review before it becomes canonical. The creator must still lock SOL for the
candidate. If review rejects the candidate as duplicate or invalid, the locked SOL
is not released immediately; it remains locked until the normal lock period ends.

Each canonical page has at most one active recommendation cycle at a time. If no
recommender SOL remains locked on the active cycle and the cycle has 90 days with
no new support, it becomes eligible for inactive status. A new eligible user can
then lock at least the required `0.2 SOL` minimum to reactivate the
recommendation. Reactivation preserves the canonical page, discoverer credit,
previous supporters, badges, and recommender history.

Reactivation does not require moderation review by default when the page is
valid, inactive, and undisputed. Reactivation requires review first if the page is
flagged, disputed, duplicate-reported, or has unsafe metadata, unsafe links, or
other integrity issues.

### Curator Stake

A curator creates a book or series recommendation by locking at least `0.2 SOL`
for a minimum of two weeks. `0.2 SOL` is the MVP minimum, not an exact stake;
there is no maximum deposit cap on locked recommender SOL.

This rule applies to recommender participants with locked SOL, not ordinary
supporters contributing `0.01 SOL`. A recommender participant must have either
`0 SOL` locked or at least `0.2 SOL` locked. Later top-ups above an existing
qualifying locked balance must be at least `0.05 SOL`.

The lock acts as spam resistance and a signal of conviction. Extra locked SOL
must not be presented as guaranteed yield, guaranteed rewards, or uncapped
influence.

The original discoverer and prior reactivators are historical recommenders for
that page. They may lock additional SOL at any time to increase their share of
future upvote/support credit, but additional stake must not rewrite past support
credit, badges, discoverer credit, or reputation history.

If extra locked SOL affects future upvote/support credit, rewards, ranking, or
visibility, it must use diminishing returns rather than linear weighting. The
exact curve and parameters remain unresolved.

Users who have never activated or reactivated a page cannot stake into that page
while it is active. They must wait until the current recommendation cycle becomes
inactive and then reactivate it by locking at least the required `0.2 SOL`
minimum.

Partial stake withdrawals do not start the inactivity window while any
recommender SOL remains locked, including the required base stake currently set
at `0.2 SOL`. If a withdrawal would leave no SOL locked on the active cycle,
Beacon must warn the recommender that the page can become inactive after 90 days
with no new support.

Withdrawals must not leave a recommender locked balance above `0 SOL` but below
`0.2 SOL`. A withdrawal that would cross below `0.2 SOL` must either be rejected
or treated as a full withdrawal to `0 SOL` with the full-withdrawal warning.

### Support / Upvote

Users support a recommendation by contributing a fixed `0.01 SOL` for MVP.

Support is not a refundable vote. It represents conviction and may make the supporter eligible for milestone rewards, badge upgrades, and reputation.

### NFT Badge

Each supporter should receive an NFT badge or equivalent on-chain collectible
proving participation in a specific book or series recommendation.

The badge represents support history, not ownership of the book or its intellectual property.

Draft badge tiers:

* Bronze when the recommendation reaches 100 supporters.
* Silver when the recommendation reaches 1,000 supporters.
* Gold when the recommendation reaches 10,000 supporters.
* Diamond when the recommendation reaches 100,000 supporters.

### Public Treasury Dashboard

The MVP should expose treasury state publicly.

At minimum:

* Community treasury balance
* Operating reserve balance
* Total SOL staked
* Available liquidity
* Lifetime recommendations
* Lifetime support transactions
* Custody/control status for major balances
* Program, treasury, multisig, governance, and upgrade authority addresses where
  applicable

The MVP must not imply full decentralization if some authorities remain under
team or multisig control. It should clearly distinguish balances controlled by
Solana program rules from balances or authorities still controlled by humans.

### Basic Governance Eligibility

At launch, governance should be limited to wallets that have interacted with Beacon.

Initial governance can be off-chain or semi-on-chain while the rules are being validated, but the model should be designed for transparent public voting.

### Trust-Minimized Custody

The MVP should design user economic flows so trust-sensitive SOL is held in
program-controlled accounts wherever feasible. This includes curator stake locks,
support contribution accounting, reward pools, and Community Treasury balances.

If any MVP flow still depends on team-controlled, company-controlled,
server-controlled, or manually administered custody, that dependency must be
visible in the spec, product copy, and launch risk review.

### Production-Like Hosting Validation

Before public beta, the MVP should run in a low-cost production-like environment
that validates the full Nuxt, Django, PostgreSQL, and Solana integration path
without implying final production reliability.

Initial hosting assumptions:

* Nuxt frontend on Vercel free tier.
* Django API on Render free tier, with Google Cloud Run as an alternative if
  Docker deployment and faster scale-to-zero cold starts are preferred.
* PostgreSQL on a dedicated managed free tier such as Neon or Aiven.

The MVP must document free-tier limits, including backend cold starts, database
retention assumptions, manual provider setup, production secret configuration,
and any Solana event monitoring that cannot safely run on a sleeping web service.

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

* Users create book or series recommendations despite the stake requirement.
* Users support recommendations even when financial rewards are uncertain.
* NFT badges and curator profiles create non-financial motivation.
* The treasury model is understandable and publicly verifiable.
* Users can see whether key balances are program-controlled,
  multisig-controlled, governance-controlled, or manually administered.
* Abuse patterns are measurable and manageable before expansion.

## Open Questions

* What exact diminishing-returns curve, cap, or fixed staking window should apply
  to additional historical recommender stake?
* Should locked curator stake yield go entirely to the treasury or be split?
* What exact duplicate-risk scoring and matching algorithm should be used?
* What metadata source should be used for enrichment after canonical identity is
  based on title, authors, and work-or-series review?
* What manual review service level is acceptable for duplicate-risk candidates
  and review-blocked reactivations?
* Which MVP balances and authorities must be program-controlled before launch?
* Which early-stage authorities can remain under disclosed multisig control?
* Should Solana event monitoring run in Django, a separate worker/indexer,
  scheduled jobs, or direct Nuxt client RPC reads during the production-like MVP?
