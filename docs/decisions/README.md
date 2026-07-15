# Decision Records

This directory tracks important Beacon decisions.

Use decision records for product, business, tokenomics, governance, treasury,
architecture, API, contract, infrastructure, security, or launch decisions that
future humans and agents should not silently re-decide.

## Format

Decision records use sequential filenames:

```text
0001-books-first-mvp.md
0002-no-governance-token-at-launch.md
```

Each record should include:

- Status: `Proposed`, `Accepted`, `Superseded`, `Deprecated`, or `Rejected`.
- Date.
- Context.
- Decision.
- Alternatives considered.
- Consequences.
- Links to relevant specs.

## Index

| ID | Decision | Status |
| --- | --- | --- |
| 0001 | [Books-first MVP](0001-books-first-mvp.md) | Accepted |
| 0002 | [Canonical book pages](0002-canonical-book-pages.md) | Accepted |
| 0003 | [Discovery-first positioning](0003-discovery-first-positioning.md) | Accepted |
| 0004 | [No governance token at launch](0004-no-governance-token-at-launch.md) | Accepted |
| 0005 | [Treasury and operating reserve split](0005-treasury-operating-reserve-split.md) | Proposed |
| 0006 | [Conservative native SOL staking preference](0006-conservative-native-sol-staking.md) | Proposed |
| 0007 | [Password session auth foundation](0007-password-session-auth-foundation.md) | Accepted |
| 0008 | [Trust-minimized protocol custody](0008-trust-minimized-protocol-custody.md) | Proposed |
| 0009 | [Google social auth strategy](0009-google-social-auth-strategy.md) | Accepted |
| 0010 | [MVP free hosting stack](0010-mvp-free-hosting-stack.md) | Proposed |
| 0011 | [Hybrid recommendation lifecycle](0011-hybrid-recommendation-lifecycle.md) | Accepted |
| 0012 | [Canonical work and series identity](0012-canonical-work-series-identity.md) | Accepted |
| 0013 | [Recommendation inactivity window](0013-recommendation-inactivity-window.md) | Accepted |
| 0014 | [Reactivation moderation policy](0014-reactivation-moderation-policy.md) | Accepted |
| 0015 | [Minimum recommender stake with no deposit cap](0015-minimum-recommender-stake-no-deposit-cap.md) | Accepted |
| 0016 | [Diminishing returns for extra recommender stake](0016-diminishing-returns-for-extra-recommender-stake.md) | Accepted |
| 0017 | [Recommender stake balance and top-up minimums](0017-recommender-stake-balance-and-top-up-minimums.md) | Accepted |
| 0018 | [Fixed support contribution](0018-fixed-support-contribution.md) | Accepted |
| 0019 | [Step-based milestone rewards](0019-step-based-milestone-rewards.md) | Accepted |
| 0020 | [Review agent design](0020-review-agent-design.md) | Accepted |
| 0021 | [Lead developer agent design](0021-lead-developer-design.md) | Accepted |
| 0022 | [Planner agent design](0022-planner-agent-design.md) | Accepted |

## Maintenance Rules

- Add a decision record when a meaningful product, business, or technical choice
  is made.
- Do not delete old records; supersede them with a newer record.
- Keep this index updated when adding or changing decision records.
- If a decision is still uncertain, use `Proposed` and link to open questions.
