# 0001: Books-First MVP

## Status

Accepted

## Date

2026-06-21

## Context

Beacon's long-term thesis can apply to many content categories, but launching
with too many categories would make discovery quality, metadata, rankings,
licensing, and user behavior harder to validate.

Books are structured, searchable, culturally rich, and a good first test of
whether people will financially and reputationally back recommendations they
believe in.

## Decision

Beacon's MVP will focus exclusively on books.

Other categories, such as movies, games, music, podcasts, courses, AI-generated
content, and independent creator projects, remain future expansion options after
the books marketplace validates the core loop.

## Alternatives Considered

### Multi-category launch

- Pros: Larger initial surface area and more user interests.
- Cons: Higher product complexity, harder moderation, weaker initial focus, and
  more metadata and ranking edge cases.
- Rejected for MVP.

### Start with a different category

- Pros: Some categories may have stronger fandom or market liquidity.
- Cons: Books are simpler to scope and align well with long-term curation
  reputation.
- Rejected for MVP.

## Consequences

- Product, API, ranking, and contract design should prioritize book discovery.
- Non-book categories should not be implemented until explicitly scoped.
- Docs and UI should avoid implying broad category support in the MVP.

## Related Specs

- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/product/user-stories.md`
