# Assistant Handoff

This file is a short-lived handoff index for agents. It is not a source of
truth and must not override product specs, architecture docs, decision records,
plans, API docs, or the changelog.

Use it only for transient context that helps the next assistant continue a
session. Move durable information to the canonical documents below, then delete
the temporary note from this file.

## Canonical Documents

- Product scope and positioning: `docs/product/vision.md`,
  `docs/product/mvp.md`, and `docs/product/user-stories.md`.
- Product policy questions and assumptions: `docs/product/open-questions.md`
  and `docs/product/assumptions.md`.
- Roadmap and implementation tracking: `docs/product/roadmap.md` and
  `docs/plans/`.
- Architecture direction: `docs/architecture/system-design.md`.
- API behavior: `docs/api/openapi.md`.
- Testing workflow: `docs/development/testing.md`.
- Decisions and history: `docs/decisions/` and `CHANGELOG.md`.
- Agent workflow rules: `AGENTS.md`.

## Temporary Notes

- Keep notes brief, dated when useful, and delete them once resolved.
- Do not record permanent decisions here; add or update a decision record.
- Do not record completed work here; update `CHANGELOG.md` or the relevant plan.
- Do not duplicate setup instructions; update the owning README or testing doc.
