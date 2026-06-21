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

## Maintenance Rules

- Add a decision record when a meaningful product, business, or technical choice
  is made.
- Do not delete old records; supersede them with a newer record.
- Keep this index updated when adding or changing decision records.
- If a decision is still uncertain, use `Proposed` and link to open questions.
