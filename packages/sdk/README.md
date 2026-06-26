# Beacon SDK

This package is reserved for a future shared Beacon client SDK.

Current status:

- No SDK source code is implemented here yet.
- No package build, publishing, or generated API client workflow is configured yet.
- Frontend API calls currently live in `apps/web`.

Implementation boundaries:

- Treat public SDK interfaces as stable contracts once introduced.
- Source API shapes from the backend API documentation in `docs/api/openapi.md` and shared types once those are implemented.
- Do not encode product, reward, staking, treasury, badge, or governance behavior that is not documented in the canonical product specs.
