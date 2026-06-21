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
| Book page model | One canonical page per book | Accepted | See `docs/decisions/0002-canonical-book-pages.md`. |
| Curator stake | At least `0.2 SOL` locked for two weeks | Draft | Needs price, abuse, and UX review. |
| Support contribution | `0.01 SOL` per support/upvote | Draft | Needs price, fee, and accessibility review. |
| Support semantics | Support is conviction, not a refundable vote | Accepted | Core positioning and risk-control language. |
| Badge semantics | Badge proves participation and discovery history | Accepted | Must not imply book, IP, or cover-art ownership. |
| Badge tiers | Bronze 100, Silver 1,000, Gold 10,000, Diamond 100,000 | Draft | Needs UX, metadata, and contract feasibility review. |
| Reward model | Milestone-based curator, early supporter, and treasury splits | Needs simulation | See `docs/tokenomics/rewards.md`. |
| Treasury split | 80% Community Treasury, up to 20% Operating Reserve | Proposed | Applies only to treasury inflows. |
| Staking strategy | Prefer native SOL staking over DeFi yield | Proposed | Requires security/legal review before launch. |
| Governance model | Participation-based governance, no launch token | Accepted | See `docs/decisions/0004-no-governance-token-at-launch.md`. |
| Revenue changes | New revenue streams require community approval | Draft | Needs governance rules and implementation detail. |

## Maintenance Rules

- Add new assumptions here when product or implementation work depends on them.
- Promote assumptions to `Accepted` only after the required confirmation or
  review happens.
- If an assumption becomes a durable decision, add or update a decision record in
  `docs/decisions/`.
