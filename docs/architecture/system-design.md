# System Design

Beacon should begin as a modular monolith with carefully limited on-chain responsibilities.

## System Boundaries

Beacon has three main system layers:

* Web application for user experience and wallet interaction.
* Backend API for product logic, metadata, search, ranking, and governance records.
* Solana contracts for trust-sensitive economic state.

## On-Chain Responsibilities

Only economic actions that require public verifiability or trust-minimized execution should live on-chain.

Potential on-chain responsibilities:

* Curator stake locking and release.
* Support transaction accounting.
* Reward pool accounting.
* Treasury and operating reserve splits.
* Badge minting or badge eligibility proofs.
* Governance vote records for major economic decisions.

On-chain programs must treat all account data and metadata as untrusted input.

Trust-sensitive funds should be held in program-controlled Solana accounts, such
as PDAs, rather than founder, company, or backend-controlled wallets. These
accounts should have no private key and should move funds only through Beacon's
documented program logic.

The on-chain trust boundary should cover:

* Custody of user deposits and support contributions before allocation.
* Curator stake locking, release eligibility, and principal accounting.
* Reward pool accounting and reward release conditions.
* Community Treasury and Operating Reserve split accounting.
* Governance-approved treasury execution where applicable.

Program upgrade authority is part of the system's economic trust model. If an
upgrade can change custody, balances, splits, rewards, lock periods, or
withdrawal rights, that authority must be documented, publicly visible, and
eventually constrained by governance or timelocks.

## Off-Chain Backend Responsibilities

The backend should handle product logic that benefits from flexibility, indexing, and iteration speed.

Responsibilities:

* Book metadata and canonical book identity.
* Duplicate detection and moderation workflows.
* Ranking and discovery algorithms.
* Search and filtering.
* Account authentication, sessions, and password reset flows.
* User profiles and reputation aggregation.
* Proposal drafts and governance metadata.
* Treasury dashboard indexing from on-chain sources.
* Analytics for abuse detection and product learning.

The backend can cache and index on-chain state, but it must not be the only source of truth for economic balances.

The backend must not be the custody authority for user deposits, curator stake
principal, reward pools, or Community Treasury funds. It may prepare transaction
data, index chain events, and present dashboards, but user-signable transactions
and program rules must remain the source of truth for trust-sensitive fund
movement.

## Frontend Responsibilities

The frontend should make economic and governance actions understandable before users sign transactions.

Responsibilities:

* Browse and search book recommendations.
* Signup, login, logout, and password reset flows.
* Create recommendation flows.
* Support/upvote flows.
* Wallet connection.
* Transaction previews.
* Badge and reputation display.
* Treasury transparency pages.
* Governance proposal and voting pages.

## MVP Hosting Shape

For the first production-like MVP environment, Beacon should prefer a simple
cross-provider free-tier deployment while the product loop is still being
validated:

* Nuxt frontend on Vercel free tier.
* Django REST API on Render free tier, unless Cloud Run is selected during
  implementation for Docker-native deployment and faster scale-to-zero cold
  starts.
* PostgreSQL on a dedicated managed free tier such as Neon or Aiven, not on a
  short-lived app-platform database if durable MVP data matters.

Expected tradeoffs:

* Free backend hosting may have cold starts after inactivity.
* Serverless PostgreSQL may require pooled connection strings or conservative
  persistent connection settings.
* A sleeping web service is not a reliable home for continuous Solana RPC
  WebSocket listeners, durable background jobs, or always-on event indexing.

Manual blocker before implementation: decide whether Solana event monitoring is
handled by Django, a separate worker/indexer, scheduled jobs, or direct Nuxt
client reads from RPC nodes. Do not invent this boundary during deployment work.

See `docs/decisions/0010-mvp-free-hosting-stack.md` and
`docs/plans/0015-mvp-free-hosting-setup.md`.

## Data Model Concepts

Core concepts for future specification:

* Book
* Recommendation
* Curator
* Supporter
* Support transaction
* Reward milestone
* Badge
* Treasury account
* Governance proposal
* Governance vote
* Reputation profile

## Economic Safety Principles

* Never sign or send transactions without explicit user approval.
* Always show recipient, amount, fee payer, cluster, and action summary before signing.
* Default to localnet or devnet during development.
* Treat wallet history and balances as weak anti-abuse signals, not identity guarantees.
* Prefer economic resistance to self-farming over invasive identity checks.
* Do not route user economic deposits through team-controlled or server-controlled
  wallets when a program-controlled account can enforce the required rules.
* Treat upgrade authority, multisig configuration, and governance execution delay
  as user-facing trust properties, not internal implementation details.

## Architecture Principle

Beacon's competitive advantage is its trust model, curation marketplace, and reputation graph, not architectural complexity.

The first implementation should keep the system simple enough to audit and explain.
