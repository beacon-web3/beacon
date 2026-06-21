# Frontend Design System Foundation

Status: Completed

## Context

Beacon needs a frontend foundation that presents the product as a books-first
discovery and reputation network, not as a speculative DeFi or yield product.
The chosen visual direction is Beacon Editorial Ledger: restrained editorial
layout, visible reputation and ledger mechanics, and clear economic disclosures
before wallet signing.

## Relevant Specs

- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/product/user-stories.md`
- `docs/product/risks.md`
- `docs/tokenomics/rewards.md`
- `docs/architecture/system-design.md`

## Design Decisions

- Use Tailwind CSS 4 CSS-first tokens in `apps/web/app/assets/css/main.css`.
- Use Nuxt UI as the component system and theme it through
  `apps/web/app/app.config.ts`.
- Use `Inter` for product UI, controls, metadata, and ledger details.
- Use `Newsreader` for editorial book titles, hero headlines, and reading
  moments.
- Support light and dark themes from the start. Dark mode should feel like a
  serious reading/editorial mode, not a terminal or crypto-console UI.
- Avoid loud gradients, neon palettes, gamified reward language, and profit-first
  presentation.

## Tasks

- [x] Inspect the existing Nuxt, Tailwind, and Nuxt UI setup.
- [x] Replace starter CSS with Beacon design tokens, typography, theme palettes,
  base styles, and reusable utility classes.
- [x] Configure Nuxt UI semantic colors and component defaults for restrained
  editorial UI.
- [x] Replace starter shell styling with Beacon navigation, footer, and theme
  behavior.
- [x] Rebuild the landing page as a representative system application with book,
  reputation, support, and ledger sections.
- [x] Reframe starter locale copy away from yield/profit/casino language.
- [x] Run lint, typecheck, and build verification.

## Acceptance Criteria

- The app uses Tailwind CSS 4 `@theme` tokens for the Beacon design foundation.
- Nuxt UI is configured with Beacon-specific semantic colors and component
  defaults.
- Inter and Newsreader are the active font families.
- Light and dark modes are supported without neon or terminal aesthetics.
- The landing page demonstrates book-first hierarchy, secondary reputation
  signals, and clear ledger mechanics.
- Visible copy avoids passive-yield, guaranteed-return, and profit-first framing.
- Frontend lint, typecheck, and build pass or any failures are documented with
  root cause.

## Verification

- `pnpm lint`
- `pnpm typecheck`
- `pnpm build`

All verification commands passed on 2026-06-21. `pnpm build` completed with
non-fatal Vite/Nuxt sourcemap warnings and a standard chunk-size warning.
