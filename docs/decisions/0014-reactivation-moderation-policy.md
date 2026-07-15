# 0014: Reactivation Moderation Policy

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's hybrid recommendation lifecycle allows an inactive canonical standalone
book work or recognized series page to be reactivated by a new eligible
recommender who locks at least the required `0.2 SOL` minimum.

The MVP needs to decide whether every reactivation should require manual
moderation. Beacon already applies duplicate-risk and manual-review gates during
candidate page creation, and reactivation operates on an existing canonical page
rather than creating a new identity. Requiring review for every reactivation
would slow discovery and add operational burden during the MVP.

## Decision

For MVP, inactive recommendation reactivation does not require moderation review
by default.

If a canonical page is valid, inactive, and not under dispute, an eligible user
can reactivate it immediately by locking at least the required `0.2 SOL`
minimum.

Moderation review is required before reactivation only when the page is flagged,
disputed, duplicate-reported, or has unsafe metadata, unsafe links, or other
integrity issues that require human review.

This decision does not resolve reward split formulas across historical
recommenders or the exact moderation service level for flagged or disputed pages.
`0015-minimum-recommender-stake-no-deposit-cap.md` resolves the MVP minimum stake
required for reactivation.

## Alternatives Considered

### Manual review for every reactivation

- Pros: Strongest control over stale, low-quality, or disputed pages.
- Cons: Creates operational friction; delays discovery; duplicates checks already
  happen at page creation; staked SOL already adds spam resistance.
- Rejected for MVP.

### No moderation gate for any reactivation

- Pros: Simplest and fastest reactivation flow.
- Cons: Unsafe for pages with active duplicate reports, disputes, unsafe links, or
  metadata integrity problems.
- Rejected in favor of exception-based review.

### No default review with exception-based moderation

- Pros: Keeps normal reactivation lightweight while preserving a safety gate for
  flagged, disputed, duplicate-reported, or unsafe pages.
- Cons: Requires backend/UI state for moderation blockers and clear user copy.
- Accepted for MVP.

## Consequences

- Reactivation UX can be immediate for valid, inactive, undisputed pages.
- Backend models and APIs need page-level moderation or integrity states that can
  block reactivation when human review is required.
- Frontend copy must distinguish ordinary inactive pages from pages whose
  reactivation is blocked by flags, duplicate reports, disputes, unsafe metadata,
  or unsafe links.
- Product docs should no longer list default reactivation moderation as an
  unresolved question.
- Moderation service levels and escalation workflows for blocked reactivations
  remain unresolved.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
