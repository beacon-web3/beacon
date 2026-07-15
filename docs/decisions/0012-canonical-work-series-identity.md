# 0012: Canonical Work And Series Identity

## Status

Accepted

## Date

2026-07-09

## Context

Beacon's canonical page model requires duplicate recommendations to converge on a
single public page. The product object is not always an ISBN, edition,
translation, or single volume. Readers often discover and recommend a standalone
book work or an entire recognized book series as the meaningful unit of cultural
discovery.

If Beacon allows separate pages for editions, translations, volumes, box sets, or
near-duplicate title spellings during the MVP, support, badges, discoverer
credit, and recommender history can fragment before the marketplace has enough
moderation and metadata infrastructure to resolve disputes cleanly.

## Decision

Beacon MVP canonicalizes recommendations around either a standalone book work or
a recognized book series.

For MVP, a recognized series receives one series-level canonical page. Individual
volume pages inside that series are not allowed. Beacon may revisit volume-level
pages later only through an explicit product or governance decision.

Users create a candidate page by entering a title and author or authors. Beacon
runs a high-sensitivity duplicate-risk check before immediate page creation.

If duplicate risk is low, the page can be created immediately and users can later
report duplicates.

If duplicate risk is detected, Beacon must show the creator the likely duplicate
page or pages and explain the risk before they continue. If the creator proceeds
anyway, the candidate page does not become canonical until manual review approves
it.

A creator who submits a risky candidate must still lock the required SOL. If
manual review rejects the candidate as a duplicate or invalid page, the locked
SOL is not released immediately; it remains locked until the normal lock period
ends. The UI must warn the creator about this consequence before they proceed.

## Alternatives Considered

### ISBN-first canonical identity

- Pros: Stable identifier when available; easy to validate many published
  editions.
- Cons: Splits editions, translations, and series-level discovery; poor fit for
  books without clean ISBN data.
- Rejected for MVP as the primary identity model.

### External metadata provider ID as canonical identity

- Pros: Can provide rich metadata and faster enrichment.
- Cons: Creates provider dependency; provider records may split works, volumes,
  editions, or translations differently from Beacon's product model.
- Rejected as the primary identity model. External IDs can still support
  duplicate detection and metadata enrichment after provider policy is chosen.

### Title and author matching only

- Pros: Low-friction creation; no provider dependency.
- Cons: Too easy to create duplicates through spelling variants, subtitles,
  translations, series names, and author-name variations.
- Rejected as a standalone control, but accepted as the user-facing input basis
  with duplicate-risk detection and manual review.

### Manual review for every page

- Pros: Strong quality control and duplicate prevention.
- Cons: Slows down low-risk creation and increases operating load.
- Rejected for all pages. Accepted for duplicate-risk candidates.

### Allow both series-level and volume-level pages

- Pros: Lets users recommend a specific volume when it has distinct cultural
  relevance.
- Cons: Creates immediate ambiguity and support fragmentation for the MVP.
- Rejected for MVP. Requires explicit future product or governance approval.

## Consequences

- Product copy, models, APIs, and UI should use language that supports both
  standalone works and series-level canonical pages.
- Duplicate detection should be high-sensitivity and treated as a risk signal, not
  an automatic final authority.
- Manual review workflows become required for disputed candidate pages.
- Page creation must clearly warn users when a risky submission can keep SOL
  locked through the normal lock period even if the page is rejected.
- Backend schema planning should account for canonical page type, normalized title
  and author fields, duplicate-risk status, manual-review status, and duplicate
  reports.
- The exact duplicate detection algorithm, metadata provider, and moderation
  service-level expectations remain implementation details to design before code.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/assumptions.md`
- `docs/product/open-questions.md`
- `docs/architecture/system-design.md`
- `docs/plans/0016-recommendation-lifecycle-data-model.md`
