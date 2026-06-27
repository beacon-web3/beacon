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

As a curator, I want to create a book recommendation by locking SOL so that my recommendation carries a stronger signal than a normal post.

Acceptance criteria:

* I can submit a book recommendation with required metadata.
* I can see the amount and duration of the required stake before confirming.
* I can see when my stake unlocks.
* I receive permanent discoverer credit if I am the first valid curator for that book.

## Supporter

As a supporter, I want to support a book with a small SOL contribution so that I can publicly signal conviction and potentially earn reputation or rewards if the book becomes widely supported.

Acceptance criteria:

* I can see the support cost before confirming.
* I can see my supporter number for the book.
* I receive a badge or collectible proving support.
* I can see the next reward or badge milestone.

## Early Supporter

As an early supporter, I want my early support to be visible so that my taste and discovery record can compound over time.

Acceptance criteria:

* My profile shows successful early support history.
* Book pages show early supporter cohorts.
* Badges upgrade when book milestones are reached.

## Reader

As a reader, I want to browse books ranked by community conviction so that I can find books worth my attention.

Acceptance criteria:

* I can browse trending and highly supported books.
* I can inspect who discovered and supported a book early.
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
