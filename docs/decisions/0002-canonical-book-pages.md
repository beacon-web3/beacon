# 0002: Canonical Book Pages

## Status

Accepted

## Date

2026-06-21

## Context

Beacon needs to avoid fragmented duplicate recommendation markets for the same
book. Repeated rounds for the same book would split reputation, confuse reward
eligibility, and create abuse opportunities.

## Decision

Each book should have one canonical Beacon page.

The first valid curator to create the page receives permanent discoverer credit.
Later users support the existing page rather than creating separate competing
recommendation pages for the same book.

## Alternatives Considered

### Repeated recommendation rounds

- Pros: Lets multiple curators compete around the same book.
- Cons: Fragments support, weakens discoverer reputation, complicates reward
  accounting, and increases duplicate spam.
- Rejected.

### Multiple curator pages per book

- Pros: Allows personal recommendation essays and competing narratives.
- Cons: Harder to define canonical rewards and support milestones.
- Rejected for MVP; could be revisited as a social layer later.

## Consequences

- Duplicate detection and canonical book identity become important requirements.
- Discoverer credit must be immutable unless fraud, abuse, or moderation policy
  requires intervention.
- Product copy should distinguish the original curator from later supporters.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/architecture/system-design.md`
