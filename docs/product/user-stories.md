# User Stories

## Account User

As a reader, curator, or supporter, I want to create and access a Beacon account
so that my discovery history can persist before wallet-based Solana actions are
enabled.

Acceptance criteria:

* I can sign up with email, username, display name, and password.
* I can log in with either email or username plus password.
* I can start Google sign-in or signup from the auth screens.
* If my verified Google email matches an existing Beacon account, Beacon links
  the Google identity to that account and logs me in.
* If my verified Google email has no Beacon account, Beacon creates an account
  with a generated username and logs me in.
* I understand social auth is account access only, not wallet identity, Solana
  account ownership proof, or anti-sybil proof.
* I can log out and confirm my current authenticated account.
* I can request a password reset without Beacon revealing whether an email has an
  account.
* I understand wallet connection comes later, before any on-chain action.

## Curator

As a curator, I want to create a book or series recommendation by locking SOL so
that my recommendation carries a stronger signal than a normal post.

Acceptance criteria:

* I can submit a standalone book work or recognized book series recommendation
  with required metadata.
* If I submit a recognized series, Beacon treats the series page as canonical and
  does not create separate MVP pages for individual volumes.
* Beacon checks my submitted title and author or authors for duplicate risk before
  immediate page creation.
* If duplicate risk is low, my page can be created immediately and other users can
  later report duplicates.
* If duplicate risk is detected, I can see likely duplicate pages and understand
  that proceeding sends my candidate page to manual review.
* If I proceed with a duplicate-risk candidate, I understand my locked SOL remains
  locked for the normal lock period even if manual review rejects the page.
* I can see the amount and duration of the required stake before confirming.
* I can see when my stake unlocks.
* If I withdraw only part of my locked SOL and some SOL remains locked, I
  understand that this does not start the inactivity window.
* If I try to withdraw all locked SOL from an active recommendation cycle, Beacon
  warns me that the recommendation can become inactive after 90 days with no new
  support.
* I receive permanent discoverer credit if I am the first valid curator for that
  standalone work or series page.
* If I discovered or previously reactivated a page, I can lock additional SOL to
  increase my share of future upvote/support credit.
* Adding more SOL does not change past supporter credit, badges, or discoverer
  history.

## Reactivator

As a curator, I want to reactivate an inactive book or series recommendation by
locking SOL so that useful works or series can regain active recommendation
status without losing their history.

Acceptance criteria:

* I can see whether a recommendation page is active or inactive.
* I can see that a recommendation becomes eligible for inactive status only after
  no recommender SOL remains locked and 90 days pass with no new support.
* I can reactivate an inactive recommendation by locking the required base stake.
* I cannot become a new staked recommender for a page while another active
  recommendation cycle is still active.
* After reactivation, the page still shows the original discoverer, prior
  reactivators, supporters, badges, and support history.
* After reactivation, I become part of that page's historical recommender set.

## Supporter

As a supporter, I want to support a book or series recommendation with a small
SOL contribution so that I can publicly signal conviction and potentially earn
reputation or rewards if the recommendation becomes widely supported.

Acceptance criteria:

* I can see the support cost before confirming.
* I can see my supporter number for the recommendation.
* I receive a badge or collectible proving support.
* I can see the next reward or badge milestone.
* My support is credited to the recommendation state that existed when I
  supported it, and later stake changes do not rewrite that history.

## Early Supporter

As an early supporter, I want my early support to be visible so that my taste and discovery record can compound over time.

Acceptance criteria:

* My profile shows successful early support history.
* Recommendation pages show early supporter cohorts.
* Badges upgrade when book milestones are reached.

## Reader

As a reader, I want to browse book and series recommendations ranked by community
conviction so that I can find works worth my attention.

Acceptance criteria:

* I can browse trending and highly supported recommendations.
* I can distinguish standalone book pages from series-level pages.
* I can inspect who discovered a book, who previously reactivated it, and who
  supported it early.
* I can distinguish active recommendation status from historical discovery and
  reactivation history.
* I can distinguish community recommendations from sponsored placements if sponsorships are later approved.

## Treasury Viewer

As any user, I want to see Beacon's treasury and staking state so that I do not need to trust hidden claims about platform funds.

Acceptance criteria:

* I can see community treasury, operating reserve, staked SOL, and available liquidity.
* I can inspect treasury inflows and outflows.
* I can distinguish funds allocated to community use from funds allocated to operating reserve.

## Governance Participant

As a participant, I want to vote on major economic and policy decisions so that Beacon's monetization and treasury use remain community-legible.

Acceptance criteria:

* I can vote only if my wallet has interacted with Beacon.
* I can review proposal details before voting.
* I can vote on new revenue streams, large treasury spending, and governance changes.
* I am not asked to vote on routine technical implementation details.

## Beacon Team

As the Beacon team, we need a transparent operating reserve so that development, audits, infrastructure, and support can be funded without hidden extraction.

Acceptance criteria:

* The operating reserve percentage is documented before launch.
* Operating reserve inflows are publicly visible.
* Community treasury spending remains separate from team-controlled operating funds.

## Future Publisher or Sponsor

As a publisher, author, or studio, I may want to pay for clearly labeled visibility if the community approves sponsored discovery revenue.

Acceptance criteria:

* Sponsored placements are impossible to confuse with organic community rankings.
* Sponsorship rules are approved through governance before activation.
* Sponsored revenue destination is visible.
