# 0002: Canonical Book Pages

## Status

Accepted

## Date

2026-06-21

## Context

Beacon needs to avoid fragmented duplicate recommendation markets for the same
book work or book series. Repeated rounds for the same work or series would split
reputation, confuse reward eligibility, and create abuse opportunities.

## Decision

Each standalone book work or recognized book series should have one canonical
Beacon page.

The first valid curator to create the page receives permanent discoverer credit.
Later users support or, when eligible, reactivate the existing page rather than
creating separate competing recommendation pages for the same work or series.

This decision is amended by `0011-hybrid-recommendation-lifecycle.md`, which
adds active recommendation cycles and historical recommender staking rights while
preserving the canonical page and permanent discoverer credit model.

This decision is further specified by `0012-canonical-work-series-identity.md`,
which defines the MVP canonical page object as either a standalone book work or a
recognized book series, not an edition, ISBN, translation, or individual volume
inside a series.

## Alternatives Considered

### Repeated recommendation rounds

- Pros: Lets multiple curators compete around the same work or series.
- Cons: Fragments support, weakens discoverer reputation, complicates reward
  accounting, and increases duplicate spam.
- Rejected.

### Multiple curator pages per work or series

- Pros: Allows personal recommendation essays and competing narratives.
- Cons: Harder to define canonical rewards and support milestones.
- Rejected for MVP; could be revisited as a social layer later.

## Consequences

- Duplicate detection and canonical book or series identity become important
  requirements.
- Discoverer credit must be immutable unless fraud, abuse, or moderation policy
  requires intervention.
- Product copy should distinguish the original discoverer, historical
  recommenders, active recommendation status, and later supporters.

## Related Specs

- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/architecture/system-design.md`
