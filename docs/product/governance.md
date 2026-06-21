# Governance

Beacon governance should protect trust without turning every product decision into a vote.

## Objective

Governance exists to give active participants control over major economic and policy decisions, especially decisions that affect treasury use, revenue models, and platform trust.

It should not slow down normal product development or technical execution.

## Eligibility

The initial governance principle is participation-based eligibility.

A wallet should be eligible to vote only if it has interacted with Beacon, such as by:

* Creating a recommendation.
* Supporting a recommendation.
* Holding a Beacon badge.
* Participating in a previous eligible governance action.

Beacon should avoid launching with a governance token at the start. Token voting can disconnect governance power from actual usage and may attract speculation before the discovery product is validated.

## Voting Weight

Equal wallet voting is simple but vulnerable to Sybil attacks.

Future voting weight may consider reputation signals:

* Number of valid recommendations created.
* Successful discovery badges.
* Support history.
* Longevity on the platform.
* Historical participation in governance.

This needs careful design before implementation. The MVP can start with simpler eligibility and collect data.

## Decision Categories

### Constitutional Decisions

High-impact rules that shape Beacon's trust model.

Examples:

* New revenue models.
* Changes to treasury split rules.
* Changes to governance eligibility.
* Changes to operating reserve policy.

Draft threshold: supermajority, such as 66% approval.

### Treasury Decisions

Community treasury allocation decisions.

Examples:

* Grants.
* Reading competitions.
* Curator awards.
* Marketing campaigns.
* Community partnerships.

Draft threshold: simple majority, subject to quorum.

### Operational Decisions

Execution decisions handled by the Beacon team.

Examples:

* UI changes.
* Technical architecture.
* Bug fixes.
* Security patches.
* Infrastructure providers.
* Search implementation details.

These should not require community votes unless they materially affect treasury, revenue, or user rights.

## Revenue Approval Rule

Beacon should establish a clear rule:

> No new revenue source may be activated without community approval.

This helps protect users from hidden monetization changes and supports Beacon's trust positioning.

Revenue sources that should require approval include:

* Affiliate links.
* Sponsored placements.
* Premium analytics.
* Publisher campaigns.
* Any new platform fee.

## Governance Anti-Patterns

Avoid:

* Voting on every small product decision.
* Monthly renegotiation of the team's operating reserve.
* Governance token launch before product-market validation.
* Hidden monetization followed by retroactive approval.
* Proposals that are too vague to evaluate.

## Open Questions

* What is the minimum participation required to vote?
* Should voting be one eligible wallet, one vote for MVP?
* What quorum is required for each decision type?
* Should badge tier or curator reputation affect vote weight?
* Which governance system should be used on Solana?
