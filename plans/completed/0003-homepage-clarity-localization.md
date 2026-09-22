# Homepage Clarity And French Localization

## Status

Completed

## Context

The current homepage introduces Beacon's tone and visual direction but does not
explain the user problem, the product mechanism, the longer-term vision, or the
roadmap clearly enough for visitors who are new to decentralized discovery.

The language switcher currently offers English and Persian. The requested update
is to remove Persian and replace it with French.

## Source Specs

- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/roadmap.md`
- `docs/product/risks.md`
- `docs/tokenomics/rewards.md`

## Scope

- Rebuild the homepage narrative around the problem Beacon solves, how it works,
  the product vision, the roadmap, and safety/clarity guardrails.
- Keep Beacon framed as a books-first discovery and reputation network, not as a
  passive yield product or guaranteed-return system.
- Replace Persian localization with French localization.
- Preserve the existing Nuxt, Vue, Nuxt UI, and Tailwind CSS 4 design-system
  conventions.

## Tasks

- [x] Review product specs and current frontend implementation.
- [x] Update Nuxt i18n configuration from `fa` to `fr`.
- [x] Replace Persian locale content with French locale content.
- [x] Update homepage copy and structure for beginner clarity.
- [x] Localize component labels that currently contain hardcoded English text.
- [x] Update navigation anchors to match the new homepage sections.
- [x] Verify with lint, typecheck, and production build.

## Acceptance Criteria

- The homepage clearly answers what problem Beacon solves, how Beacon works, what
  the vision is, and what roadmap phases are planned.
- The copy does not invent reward formulas, governance policy, treasury splits,
  or launch promises beyond documented specs.
- The language switcher offers English and French only.
- French pages render left-to-right and contain translated UI copy.
- The web app passes lint, typecheck, and build verification.

## Verification

Run from `apps/web/`:

```sh
pnpm lint
pnpm typecheck
pnpm build
```
