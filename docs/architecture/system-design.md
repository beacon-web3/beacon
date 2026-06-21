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

## Off-Chain Backend Responsibilities

The backend should handle product logic that benefits from flexibility, indexing, and iteration speed.

Responsibilities:

* Book metadata and canonical book identity.
* Duplicate detection and moderation workflows.
* Ranking and discovery algorithms.
* Search and filtering.
* User profiles and reputation aggregation.
* Proposal drafts and governance metadata.
* Treasury dashboard indexing from on-chain sources.
* Analytics for abuse detection and product learning.

The backend can cache and index on-chain state, but it must not be the only source of truth for economic balances.

## Frontend Responsibilities

The frontend should make economic and governance actions understandable before users sign transactions.

Responsibilities:

* Browse and search book recommendations.
* Create recommendation flows.
* Support/upvote flows.
* Wallet connection.
* Transaction previews.
* Badge and reputation display.
* Treasury transparency pages.
* Governance proposal and voting pages.

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

## Architecture Principle

Beacon's competitive advantage is its trust model, curation marketplace, and reputation graph, not architectural complexity.

The first implementation should keep the system simple enough to audit and explain.
