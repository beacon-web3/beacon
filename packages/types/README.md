# Beacon Types

This package is reserved for future shared TypeScript types used by Beacon apps and packages.

Current status:

- No shared type source files are implemented here yet.
- Frontend-local types currently live near their Nuxt components and composables.
- Backend API response contracts are documented in `docs/api/openapi.md`.

Implementation boundaries:

- Add types here when they are consumed by more than one package or generated from a documented API contract.
- Keep generated types clearly separated from handwritten domain types if generation is introduced.
- Do not use this package to define product policy that is not already documented in the canonical specs.
