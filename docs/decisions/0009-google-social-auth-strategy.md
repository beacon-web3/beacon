# Google Social Auth Strategy

Status: Accepted

Date: 2026-06-27

## Context

Beacon already uses Django session cookies for browser account access, CSRF
protection for unsafe session requests, email/password signup, email
verification, password reset, and auth throttling. The next auth increment adds
open social auth, starting with Google, while preserving Beacon's product
positioning as a books-first discovery and reputation network.

The implementation must avoid treating social auth as wallet identity, Solana
account ownership proof, anti-sybil proof, or any on-chain authorization signal.
It must also avoid exposing provider tokens to frontend code.

## Decision

Use backend-owned Django social authentication with `django-allauth`, starting
with Google only. Keep Django session cookies as the browser auth mechanism.

Google OAuth/OIDC starts from Nuxt but redirects to Google through a backend
start endpoint. The callback is handled by Django, which validates state,
exchanges the authorization code server-side, resolves the Beacon account, calls
Django `login()`, issues a CSRF cookie, and redirects back to Nuxt with only a
generic success or failure query parameter.

Beacon will auto-link a Google identity to an existing Beacon account only when
Google reports the email as verified. A verified Google email without a Beacon
account creates a new account with a generated unique username and an unusable
password. Unverified provider email claims are not used for email-based
auto-linking.

## Alternatives Considered

### Browser-Managed OAuth Tokens

- Pros: Simpler frontend-only integration for some providers.
- Cons: Exposes provider tokens to browser storage or frontend runtime, creates a
  second auth model beside Django sessions, and increases token leakage risk.
- Rejected: Beacon should keep provider tokens server-side and preserve session
  cookie auth.

### Hand-Rolled OAuth Storage and State Handling

- Pros: Full control over the persistence model and fewer package dependencies.
- Cons: OAuth state validation, provider account storage, and future provider
  differences are security-sensitive and easy to implement incorrectly.
- Rejected: A mature Django integration is safer and better aligned with the
  existing Django auth stack.

### Require Manual Linking for Matching Emails

- Pros: Avoids any automatic account linking behavior.
- Cons: Creates unnecessary friction for users who already control a verified
  email address and expect Google login/signup entry points to converge.
- Rejected: Verified provider email is sufficient for this account-auth use case;
  unverified emails remain blocked from auto-linking.

### Add GitHub and Apple Immediately

- Pros: More auth choices at launch.
- Cons: GitHub and Apple require provider-specific verified-email and operational
  handling that would expand scope before the shared contract is proven.
- Rejected: Google-first rollout keeps the initial surface smaller and provider
  expansion can follow in separate plans.

## Consequences

- Deployed environments must run Django migrations for `django.contrib.sites` and
  `django-allauth` tables.
- Backend configuration now requires Google OAuth client credentials and a
  callback redirect URI before social auth can be enabled outside local tests.
- Provider access tokens remain backend-only and are not part of Nuxt state.
- Future GitHub or Apple support should reuse the same Beacon session contract
  while adding provider-specific verified-email normalization.
- Social auth remains separate from wallet connection and on-chain identity.

## Links

- `docs/plans/0013-google-social-auth.md`
- `docs/api/openapi.md`
- `docs/product/user-stories.md`
- `docs/decisions/0007-password-session-auth-foundation.md`
