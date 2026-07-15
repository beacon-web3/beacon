# Assumptions Register

This file tracks draft assumptions that guide Beacon planning but should not be
treated as finalized implementation policy unless their status says `Accepted`.

Status values:

- `Draft`: Working assumption for discussion.
- `Needs simulation`: Requires economic or abuse-resistance modeling.
- `Needs legal review`: Requires legal or regulatory review.
- `Needs security review`: Requires security review before implementation.
- `Accepted`: Approved as current project policy.
- `Rejected`: Considered and rejected.

| Assumption | Current Value | Status | Notes |
| --- | --- | --- | --- |
| MVP content category | Books only | Accepted | See `docs/decisions/0001-books-first-mvp.md`. |
| Book page model | One canonical page per standalone book work or recognized series | Accepted | See `docs/decisions/0002-canonical-book-pages.md` and `docs/decisions/0012-canonical-work-series-identity.md`. |
| Series page model | Recognized series are series-level only for MVP | Accepted | Individual-volume pages require a future explicit product or governance decision. |
| Duplicate-risk flow | Low-risk submissions can create immediately; risky submissions require creator warning and manual review | Accepted | Rejected risky submissions keep SOL locked until the normal lock period ends. |
| Duplicate detection algorithm | High-sensitivity title/author/work-or-series matching | Draft | Exact scoring, thresholds, and review tooling remain unresolved. |
| Recommendation lifecycle | Permanent discoverer credit with single active recommendation cycles and reactivation after inactivity | Accepted | See `docs/decisions/0011-hybrid-recommendation-lifecycle.md`. |
| Reactivation moderation | No moderation review by default for valid, undisputed inactive pages | Accepted | Flagged, disputed, duplicate-reported, unsafe metadata, or unsafe link cases require review before reactivation. See `docs/decisions/0014-reactivation-moderation-policy.md`. |
| Recommender minimum stake | At least `0.2 SOL` locked for two weeks, with no maximum deposit cap | Accepted | `0.2 SOL` is the MVP minimum to activate or reactivate; recommender balances must be `0 SOL` or at least `0.2 SOL`. See `docs/decisions/0015-minimum-recommender-stake-no-deposit-cap.md` and `docs/decisions/0017-recommender-stake-balance-and-top-up-minimums.md`. |
| Historical recommender stake additions | Original discoverer and prior reactivators may add locked SOL for future upvote/support credit share | Accepted | Later top-ups above an existing qualifying balance must be at least `0.05 SOL`; extra stake must use diminishing returns if it affects future credit, rewards, ranking, or visibility. Exact formula remains unresolved. See `docs/decisions/0016-diminishing-returns-for-extra-recommender-stake.md` and `docs/decisions/0017-recommender-stake-balance-and-top-up-minimums.md`. |
| Recommendation inactivity window | No locked recommender SOL plus 90 days with no new support | Accepted | See `docs/decisions/0013-recommendation-inactivity-window.md`. |
| Support contribution | Fixed `0.01 SOL` per support/upvote for MVP | Accepted | Applies to ordinary supporters, not recommender locked SOL. See `docs/decisions/0018-fixed-support-contribution.md`. |
| Support semantics | Support is conviction, not a refundable vote | Accepted | Core positioning and risk-control language. |
| Badge semantics | Badge proves participation and discovery history | Accepted | Must not imply book, IP, or cover-art ownership. |
| Badge tiers | Bronze 100, Silver 1,000, Gold 10,000, Diamond 100,000 | Draft | Needs UX, metadata, and contract feasibility review. |
| Reward timing | Step-based milestone reward evaluation for MVP | Accepted | Exact thresholds, formulas, and splits still need simulation. See `docs/decisions/0019-step-based-milestone-rewards.md` and `docs/tokenomics/rewards.md`. |
| Treasury split | 80% Community Treasury, up to 20% Operating Reserve | Proposed | Applies only to treasury inflows. |
| Staking strategy | Prefer native SOL staking over DeFi yield | Proposed | Requires security/legal review before launch. |
| Governance model | Participation-based governance, no launch token | Accepted | See `docs/decisions/0004-no-governance-token-at-launch.md`. |
| Revenue changes | New revenue streams require community approval | Draft | Needs governance rules and implementation detail. |
| User fund custody | Trust-sensitive user deposits, curator locks, reward pools, and Community Treasury balances should use program-controlled Solana accounts where feasible | Proposed | See `docs/decisions/0008-trust-minimized-protocol-custody.md`; requires contract design and security review. |
| Early authority control | Upgrade authority or incomplete treasury automation may be team or multisig controlled only if publicly disclosed | Draft | Needs multisig threshold, signer distribution, and launch disclosure review. |
| Mature authority control | Custody-affecting upgrades and Community Treasury execution should move toward governance control with timelocks | Draft | Needs governance design, timelock duration, and transfer milestone. |
| Contract assurance | Production contracts custodying meaningful SOL should be open source, security-reviewed, and publicly documented before launch | Draft | Needs audit scope, budget, and launch-blocking criteria. |
| MVP frontend hosting | Vercel free tier for the Nuxt frontend | Proposed | Suitable for production-like MVP testing; not a production reliability guarantee. |
| MVP backend hosting | Render free tier for Django, with Cloud Run as an alternative if Docker deployment and faster cold starts are preferred | Proposed | Needs provider account setup, environment configuration, and cold-start acceptance. |
| MVP database hosting | Neon or Aiven free-tier managed PostgreSQL, selected before deployment | Proposed | Avoid disposable app-platform free databases for durable MVP data. |
| Solana event monitoring host | Undecided | Draft | Manual blocker before implementing background workers, RPC WebSocket listeners, or durable indexing. |

## Maintenance Rules

- Add new assumptions here when product or implementation work depends on them.
- Promote assumptions to `Accepted` only after the required confirmation or
  review happens.
- If an assumption becomes a durable decision, add or update a decision record in
  `docs/decisions/`.
