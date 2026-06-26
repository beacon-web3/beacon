# Scripts

This directory is reserved for repository-level automation scripts.

Current status:

- No standalone scripts are implemented here yet.
- Existing application commands live in each app's own tooling, such as `apps/api` for Django commands and `apps/web/package.json` for Nuxt scripts.

Script guidelines:

- Keep scripts deterministic and safe to run from the repository root unless documented otherwise.
- Document required environment variables, external services, and side effects in this README when adding a script.
- Prefer project-native commands for app-specific workflows before adding repository-level wrappers.
