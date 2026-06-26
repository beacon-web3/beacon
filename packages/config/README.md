# Beacon Config

This package is reserved for future shared configuration used across Beacon apps and packages.

Current status:

- No shared configuration module is implemented here yet.
- Backend configuration currently lives in `apps/api/beacon_api/settings.py`.
- Frontend runtime configuration currently lives in `apps/web/nuxt.config.ts`.

Implementation boundaries:

- Do not store secrets in this package.
- Keep environment-specific values in app-level environment variables.
- Use this package only for non-secret shared defaults, validation helpers, or constants that are needed by more than one workspace package.
