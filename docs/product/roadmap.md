# Roadmap

This roadmap is a planning document, not a delivery promise. Dates should be
added only when launch planning becomes concrete.

## Phase 0: Spec Foundation

Goal: Make the product, economics, risks, and architecture explicit before
implementation.

Key outcomes:

- Product vision, MVP scope, user stories, governance, treasury, risks, rewards,
  staking, and architecture docs exist.
- Decision records capture major product and technical choices.
- Open questions and assumptions are tracked in dedicated files.

## Phase 1: Local Prototype

Goal: Validate the basic application flow without mainnet or production-risk
assumptions.

Key outcomes:

- Users can create standalone book work or series recommendation records locally.
- Users can view canonical recommendation pages and support counts.
- API and frontend contracts are documented.
- Local tests cover the core non-chain business logic.

## Phase 2: Books MVP

Goal: Implement the books-first Beacon loop against the documented MVP scope.

Key outcomes:

- Curator stake flow is designed and tested.
- Support contribution flow is designed and tested.
- Badge and reputation behavior is specified and implemented if approved.
- Treasury dashboard exposes core balances and activity metrics.

## Phase 3: Solana Devnet Validation

Goal: Validate on-chain mechanics safely before any production deployment.

Key outcomes:

- Solana programs run on devnet or local validator.
- Transaction signing, account validation, and event indexing are tested.
- Reward and treasury accounting are reconciled against backend state.
- Security review findings are tracked before launch decisions.

## Phase 4: Economic, Legal, And Security Review

Goal: Reduce avoidable launch risk before public beta.

Key outcomes:

- Reward formulas and milestone thresholds are simulated.
- Sybil and self-farming risks are reviewed.
- Legal review covers positioning, rewards, staking, treasury, badges, and
  sponsored or affiliate revenue.
- Security review covers contracts, APIs, wallet flows, and treasury operations.

## Phase 4.5: Production-Like MVP Hosting

Goal: Stand up the lowest-cost production-like environment before public beta so
integration risks are visible without implying final production reliability.

Key outcomes:

- Nuxt frontend is deployed to Vercel.
- Django API is deployed to Render free tier or Cloud Run free tier.
- PostgreSQL runs on a dedicated managed provider such as Neon or Aiven.
- Production environment variables, CORS, CSRF, secure cookies, OAuth redirects,
  email, reCAPTCHA, and health checks are configured.
- Cold-start behavior, database retention assumptions, and Solana indexing
  blockers are documented before broader beta launch.

## Phase 5: Public Beta

Goal: Launch a constrained beta that tests real user behavior while preserving
trust and operational control.

Key outcomes:

- Books-only beta is live with clear disclaimers and public documentation.
- Treasury dashboard is public.
- Governance eligibility and initial proposal process are documented.
- Abuse monitoring and incident response processes are in place.

## Phase 6: Category Expansion Review

Goal: Decide whether Beacon should expand beyond books.

Key outcomes:

- Books MVP metrics and user behavior are reviewed.
- New category risks, metadata requirements, and ranking changes are documented.
- Community governance approves any major category expansion if required.
