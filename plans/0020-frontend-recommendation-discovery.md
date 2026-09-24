# Plan: Frontend Recommendation Discovery And Creation

## Status

Draft

## Linked Specs

- `docs/product/mvp.md` — books-first MVP scope (books only, canonical pages, curator stake, fixed 0.01 SOL support, badges).
- `docs/product/user-stories.md` — reader/curator/supporter stories for browsing, creating, and supporting recommendations.
- `docs/product/roadmap.md` — Phase 1 outcomes: create records locally, view canonical pages and support counts.
- `docs/product/assumptions.md` — cover image storage is draft (presigned S3 upload unresolved; API accepts a plain URL today).
- `docs/product/open-questions.md` — duplicate-risk flow unresolved; no duplicate-risk endpoint exists yet.
- `plans/0018-recommendation-lifecycle-api.md` — API contract implemented by the backend (endpoints, fields, envelopes).

## Objective

Implement the Nuxt frontend for the recommendation API so a reader can
discover book/series recommendations on a public list page, view a
recommendation detail page (discoverer credit, status, support count,
supports, badges), and an authenticated curator can create a book or series
recommendation with the books-first MVP fields. Wallet-dependent flows
(activation, reactivation, support confirmation, staking) are explicitly
out of scope until a wallet integration plan exists.

## Scope

In scope:

- Public discovery list at `/recommendations` with search, category filter,
  ordering, and pagination against `GET /api/recommendations/`.
- Public detail page at `/recommendations/:id` showing summary/detail fields,
  read-only support count and supports list, and public badges preview.
- Bookmark action for authenticated users (`POST /api/recommendations/:id/bookmark/`).
- Authenticated create form at `/recommendations/create` for the books-MVP
  input fields (`title`, `creator_names`, `page_type`, `description`,
  `external_reference_url`, `cover_image_url`, `categories`, `is_canonical`).
- One small backend companion task: public read-only `GET /api/categories/`
  so the create form can list categories (MVP requires "Category or genre"
  metadata; no category endpoint exists today).
- i18n for English and French, Playwright E2E coverage, CHANGELOG entry.

Out of scope:

- Wallet connection and any Solana signing (recommend/reactivate/support/confirm/stake).
  These need a wallet integration plan first; support UI is read-only until then.
- Cover image upload (presigned PUT). The form accepts a plain `cover_image_url`
  URL per the current API contract. See Open Questions.
- Duplicate-risk pre-create warning panel. The API has no duplicate-risk
  endpoint (`docs/product/open-questions.md`); the form surfaces the
  canonical-duplicate 400 from the API instead. See Open Questions.
- Non-book content types (create flow is books-only; API defaults to BOOK).

## Dependencies

- Product decisions: MVP scope (books only), fixed `0.01 SOL` support cost,
  badge semantics (participation, not ownership), support-as-conviction
  guardrail copy.
- Technical decisions: no wallet library in `apps/web` yet; follow existing
  `useApiFetch` pattern for all API calls.
- Open questions: duplicate-risk flow; categories endpoint acceptance; cover
  image upload path.

## Codebase Patterns (follow these)

- **API calls**: `apps/web/app/composables/useApiFetch.ts` — `apiFetch<T>(url, { method, body, ... })` sets CSRF on unsafe methods, `Accept-Language` from i18n locale, `credentials: 'include'`, 15s timeout, throws `ApiFetchError` (has `statusCode`, `data`, `statusMessage`). Reuse; do not add another fetch wrapper.
- **Auth state**: `apps/web/app/stores/account.ts` (Pinia setup store) — `account`, `status`, `isLoggedIn`, `fetchAccount()`. Gate authed pages on `isLoggedIn`; redirect to `/login` when not.
- **Pages**: Nuxt 4 `app/` directory; pages use `<script setup lang="ts">`, `useI18n()` + `useLocalePath()`, `@nuxt/ui` v4 components (`UAlert`, `UButton`, `UIcon`, `UInput`, etc.), design tokens in templates (`text-ink`, `text-ink-muted`, `bg-paper`, `border-rule`, `beacon-container`, `beacon-panel`, `beacon-kicker`), dark mode via `dark:` variants.
- **Validation**: `zod` is already a dependency — use it for create-form client validation.
- **Tests**: Playwright only (`apps/web/tests/e2e/`), with a `helpers.ts` pattern for auth/setup. No Vitest setup.
- **Style gates**: `pnpm lint` (eslint), `pnpm typecheck` (vue-tsc), `pnpm build`.

## Phases

### Phase 1: Foundation

#### Task 1: Client types and validation schemas

Description: Add TypeScript types mirroring the recommendation API contract
(summary, detail, list envelope, supports, badges, create input) plus a zod
schema for the create form, in `apps/web/app/types/recommendations.ts`.

Acceptance criteria:

- [ ] Types match the API: `RecommendationSummary` (id, title, creator_names, content_type, page_type, status, support_count, categories, cover_image_url, created_at), `RecommendationDetail` (adds creator, current_recommender, description, external_reference_url, is_canonical, metadata + reserved fields), list envelope `{ results, count, page, page_size }`.
- [ ] Enums match backend choices: `PageType` = `STANDALONE_WORK | RECOGNIZED_SERIES`, `ContentType` = `BOOK | MOVIE | SERIES | PODCAST | GAME | APP | TECH`, `Status` from the API.
- [ ] `CreateRecommendationSchema` (zod) validates: title/creator_names required non-empty, page_type in enum, optional description/external_reference_url/cover_image_url, categories as id array, is_canonical boolean.

Verification:

- [ ] `pnpm typecheck` passes in `apps/web`.
- [ ] Manual check: types compile against a real `GET /api/recommendations/` response shape.

Files likely touched:

- `apps/web/app/types/recommendations.ts` (new)

Dependencies: None.

Estimated scope: Small.

#### Task 2: Recommendation API composable

Description: Add `useRecommendationsApi` composable wrapping `useApiFetch`
with typed methods for the in-scope endpoints, following the store/composable
style already used by `useSocialAuthStart`/`account` store.

Acceptance criteria:

- [ ] Methods exist: `listRecommendations(params)`, `getRecommendation(id)`, `createRecommendation(input)`, `updateRecommendation(id, patch)`, `listSupports(id)`, `listBadges(id)`, `bookmark(id)`.
- [ ] List params typed (page, page_size, search, category, ordering, status, page_type, creator) and serialized as query strings.
- [ ] Errors propagate as `ApiFetchError` (callers read `statusCode`/`data`); no swallowed errors.
- [ ] No new HTTP client or dependency added.

Verification:

- [ ] `pnpm typecheck` passes.
- [ ] Manual check against running API: `listRecommendations({})` returns the envelope and `getRecommendation(id)` returns summary/detail.

Files likely touched:

- `apps/web/app/composables/useRecommendationsApi.ts` (new)

Dependencies: Task 1.

Estimated scope: Medium.

#### Task 3: Backend companion — public categories endpoint

Description: Add a small read-only `GET /api/categories/` endpoint so the
create form can list categories. Expose `id`, `name`, `slug` (optionally
`content_type`) for active categories, add URL route and serializer test.

Acceptance criteria:

- [ ] `GET /api/categories/` is public (AllowAny) and returns active categories only.
- [ ] Response fields: `id`, `name`, `slug` (+ `content_type` when set); ordered by name.
- [ ] Optional `?content_type=BOOK` filter supported.
- [ ] Registered in `apps/api/recommendations/urls.py`; one serializer test covers the response shape and active-only filtering.

Verification:

- [ ] `bash scripts/test-postgres.sh tests/recommendations -q` passes (workdir `apps/api`).
- [ ] Manual check: `curl http://127.0.0.1:8000/api/categories/` returns the list.

Files likely touched:

- `apps/api/recommendations/urls.py`
- `apps/api/recommendations/views/core.py` (or a new `views/categories.py` following the views-package pattern)
- `apps/api/recommendations/serializers.py`
- `apps/api/tests/recommendations/test_recommendation_list.py` or a new categories test

Dependencies: None (backend, parallel-safe with Tasks 1-2).

Estimated scope: Small.

### Phase 2: Discovery And Detail

#### Task 4: Recommendation card component

Description: Add a presentational `RecommendationCard` component rendering
summary fields (title, creator_names, categories, support_count, status,
cover_image_url, created_at) with a link to the detail page; reuse
`BeaconBookCard.vue` styling conventions and the design tokens.

Acceptance criteria:

- [ ] Displays all summary fields; empty categories and missing cover image render gracefully.
- [ ] Whole card is a NuxtLink (locale-aware) to `/recommendations/:id`.
- [ ] Status shown with non-color-only indicator (badge text + icon), accessible label.
- [ ] Uses design tokens; no inline hex/pixel values.

Verification:

- [ ] `pnpm typecheck` and `pnpm lint` pass.
- [ ] Manual check in dev against real data: card renders, link navigates.

Files likely touched:

- `apps/web/app/components/recommendations/RecommendationCard.vue` (new)

Dependencies: Task 1.

Estimated scope: Small.

#### Task 5: Discovery list page

Description: Add `/recommendations` page fetching the list through the
composable with SSR-friendly `useAsyncData`; render the card grid, filters
(search, category select from `GET /api/categories/`, ordering), pagination
controls, and loading/empty/error states.

Acceptance criteria:

- [ ] Page is public (no auth redirect); first load renders server-side.
- [ ] Filters: free-text search (min length), category slug, ordering (`-support_count`, `created_at`, `-created_at`), reflected in page query params so URL is shareable.
- [ ] Pagination matches the envelope (`count`, `page`, `page_size`); skeleton loading state, explicit empty state, and error state with retry.
- [ ] Category select options come from `GET /api/categories/` (Task 3).
- [ ] `createRecommendation` target link visible for authenticated users.

Verification:

- [ ] `pnpm typecheck` and `pnpm lint` pass; `pnpm build` succeeds.
- [ ] Manual check: browse with filters/pagination, share URL preserves state.

Files likely touched:

- `apps/web/app/pages/recommendations/index.vue` (new)
- `apps/web/app/components/recommendations/RecommendationFilters.vue` (new, if split out)
- `apps/web/app/i18n/locales/en.json` and `fr.json`

Dependencies: Tasks 2, 3, 4.

Estimated scope: Large (split into page + filters component if needed).

#### Task 6: Recommendation detail page

Description: Add `/recommendations/:id` page fetching detail (fall back to
summary for anonymous users per API), render discoverer credit, current
recommender, status, description, external link, categories, support count
with read-only supports list, public badges preview, and a bookmark button
for authenticated users.

Acceptance criteria:

- [ ] Anonymous view uses summary response; authenticated view uses detail (creator/current_recommender rendered via account ref).
- [ ] Support section is read-only and shows the fixed `0.01 SOL` cost copy only as informational text — NO support action (wallet out of scope).
- [ ] Badge preview renders public badges; copy states badges represent Beacon participation, not book ownership.
- [ ] Bookmark POST works for authenticated users and reflects state; unauthenticated users see a login prompt instead.
- [ ] Loading, empty, and error (404) states handled.

Verification:

- [ ] `pnpm typecheck` and `pnpm lint` pass.
- [ ] Manual check: anon and authed views, bookmark toggles, 404 state.

Files likely touched:

- `apps/web/app/pages/recommendations/[id].vue` (new)
- `apps/web/app/components/recommendations/RecommendationDetailPanel.vue` (new, if split out)
- `apps/web/app/components/recommendations/SupportPreview.vue` (new)
- `apps/web/app/i18n/locales/en.json` and `fr.json`

Dependencies: Tasks 2, 4.

Estimated scope: Large (split into detail panel + support preview components).

#### Task 7: Navigation integration

Description: Add navigation entries (Discover, Create recommendation) in the
default layout and a discovery entry point on the dashboard for authenticated
users.

Acceptance criteria:

- [ ] Default layout nav shows Discover (public) and, for authenticated users, Create link.
- [ ] Dashboard links to the discovery list and the create page.
- [ ] Links are locale-aware (`useLocalePath`).

Verification:

- [ ] `pnpm lint` passes.
- [ ] Manual check: nav renders, links work for anon and authed states.

Files likely touched:

- `apps/web/app/layouts/default.vue`
- `apps/web/app/pages/dashboard.vue`

Dependencies: Tasks 5, 6.

Estimated scope: Small.

### Phase 3: Create Flow

#### Task 8: Create recommendation form component

Description: Add a `CreateRecommendationForm` component with zod client
validation for the books-MVP input fields, category multi-select from
`GET /api/categories/`, and API error surfacing (including the
canonical-duplicate 400).

Acceptance criteria:

- [ ] Fields: title, creator_names, page_type (segmented STANDALONE_WORK / RECOGNIZED_SERIES), description, external_reference_url, cover_image_url, categories (multi-select), is_canonical (advanced toggle).
- [ ] Client validation via zod; field-level errors rendered accessibly.
- [ ] Server `ApiFetchError` errors rendered (e.g. canonical duplicate, invalid category scoping); submitting twice is prevented while pending.
- [ ] No wallet/stake UI — activation remains out of scope; success navigates to the new detail page.

Verification:

- [ ] `pnpm typecheck` and `pnpm lint` pass.
- [ ] Manual check: invalid submit shows field errors; valid submit redirects; duplicate canonical title shows the API error.

Files likely touched:

- `apps/web/app/components/recommendations/CreateRecommendationForm.vue` (new)
- `apps/web/app/i18n/locales/en.json` and `fr.json`

Dependencies: Tasks 2, 3.

Estimated scope: Large (verify against API contract; split field subcomponents if needed).

#### Task 9: Create page with auth guard

Description: Add `/recommendations/create` page gated on authentication
(account store); redirect to login with a return path when anonymous;
render the form after account fetch resolves.

Acceptance criteria:

- [ ] Anonymous users are redirected to `/login?redirect=/recommendations/create`.
- [ ] Authenticated users see the form; account state determines render (pending/error states reused from dashboard pattern).
- [ ] Page uses default layout and existing design conventions.

Verification:

- [ ] `pnpm lint` and `pnpm typecheck` pass.
- [ ] Manual check: anon redirect, authed form renders.

Files likely touched:

- `apps/web/app/pages/recommendations/create.vue` (new)
- `apps/web/app/i18n/locales/en.json` and `fr.json`

Dependencies: Tasks 7, 8.

Estimated scope: Small.

### Phase 4: Polish And Verification

#### Task 10: i18n complete pass (en + fr)

Description: Ensure every new string across pages/components has both English
and French entries, matching existing locale structure and writing style.

Acceptance criteria:

- [ ] No raw user-facing strings in new components/pages (all via `t()`).
- [ ] Both `en.json` and `fr.json` updated; keys consistent.
- [ ] Guardrail wording (support cost informational copy, badge = participation, discovery-network positioning) matches product copy constraints.

Verification:

- [ ] `pnpm lint` passes.
- [ ] Manual check: switch locale, new pages render in French without missing keys.

Files likely touched:

- `apps/web/app/i18n/locales/en.json`
- `apps/web/app/i18n/locales/fr.json`

Dependencies: Tasks 5, 6, 8, 9.

Estimated scope: Medium.

#### Task 11: Playwright E2E coverage

Description: Add E2E specs for the discovery list and the create flow,
reusing `tests/e2e/auth/helpers.ts` patterns: list renders, filters work,
create happy path, and anonymous create redirect.

Acceptance criteria:

- [ ] Spec: discovery list loads and shows recommendations; category filter narrows results.
- [ ] Spec: anonymous access to `/recommendations/create` redirects to login.
- [ ] Spec: authenticated user creates a recommendation and is redirected to its detail page.
- [ ] Existing specs continue to pass.

Verification:

- [ ] `pnpm test:e2e` passes (Playwright).

Files likely touched:

- `apps/web/tests/e2e/recommendations/discovery.spec.ts` (new)
- `apps/web/tests/e2e/recommendations/create.spec.ts` (new)

Dependencies: Tasks 5, 6, 8, 9.

Estimated scope: Medium.

#### Task 12: Documentation and changelog

Description: Add a CHANGELOG entry describing the frontend recommendation
discovery/creation feature and register this plan as active in
`plans/README.md`; update plan 0018 if the contract text is affected.

Acceptance criteria:

- [ ] `CHANGELOG.md` has an entry under Unreleased covering discovery, detail, create pages, categories endpoint, and the read-only support/badges surfaces.
- [ ] `plans/README.md` lists 0020 as Draft/In Progress with link.
- [ ] No product policy introduced in docs (guardrail language consistent with specs).

Verification:

- [ ] Manual check: changelog and README render correctly.

Files likely touched:

- `CHANGELOG.md`
- `plans/README.md`

Dependencies: All prior tasks.

Estimated scope: Small.

## Checkpoints

- [ ] After Phase 1: `pnpm typecheck`, `pnpm lint` pass; backend categories test passes.
- [ ] After Phase 2: discovery and detail pages work end-to-end against the running API.
- [ ] After Phase 3: authenticated create flow works end-to-end.
- [ ] Before completion: all acceptance criteria met, `pnpm build` and `pnpm test:e2e` pass, changelog and plans README updated.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Wallet flows excluded leave support button absent; users may expect it | Medium | Detail page shows read-only support copy and count; separate plan required for wallet integration before any SOL action. |
| No categories endpoint existed before this plan | Medium | Task 3 adds a minimal public read-only endpoint; scoped, no schema change. |
| Duplicate-risk pre-create warning cannot be built (no API support, product open question) | Medium | Form surfaces the API's canonical-duplicate 400 and flags the open question; no invented duplicate UI. |
| Cover image upload unresolved (assumption: draft) | Low | Form accepts plain `cover_image_url` per current contract; upload deferred to the storage decision. |
| SSR fetch of Django API with session cookies (cross-origin CORS) | Medium | Follow existing `useApiFetch` behavior (credentials include); keep first list load SSR-friendly via `useAsyncData`, verify CORS preflight in dev config. |

## Open Questions

- Wallet/Solana flows (activation, reactivation, support confirmation, staking) need a separate frontend plan after wallet connection exists. Is a wallet integration plan already queued, and should detail/support UI block on it?
- Should `GET /api/categories/` (Task 3) also expose `content_type` in list responses, or keep the summary shape minimal for the form?
- The create form's `is_canonical` handling depends on the unresolved duplicate-risk flow (`docs/product/open-questions.md`): should the form expose the toggle now, or hide it until the duplicate-risk UI decision is made?
- Cover image upload: should the create form remain plain-URL-only until the presigned PUT storage decision (`docs/product/assumptions.md`) lands?

## Conflicts With Existing Plans

None. No active plan touches `apps/web` pages/components or the categories
endpoint. Plan 0018 (recommendation lifecycle API) is Completed and is the
dependency contract; plan 0019 (factory-boy postgeneration deprecation) is
unrelated backend tooling.