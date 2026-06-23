# 0007 Password Session Auth Foundation

Status: Accepted

Date: 2026-06-21

## Context

Beacon needs account authentication beyond the initial email-only prototype.
Future product specs include user profiles, wallet addresses, reputation signals,
account credit, posts, upvotes, and possible social login. Auth must remain a
product identity foundation, not an economic balance or guaranteed-return system.

## Decision

Use Django's auth system with Beacon's `accounts.Account` as the custom user
model. Browser login uses Django session cookies. Users sign up with email,
username, display name, password, and reCAPTCHA v2 Invisible verification. Users
log in with email-or-username plus password.

The user model includes nullable `wallet_address` and reserved `reputation_score`
and `account_credit` fields. These fields do not define reward formulas,
withdrawal behavior, treasury accounting, or governance weight.

Password reset uses Django's built-in token generator, Django's email backend,
and generic request responses to avoid account enumeration.

## Alternatives Considered

- Keep email-only auth: rejected because it does not support password login,
  reset flows, or future identity providers.
- JWT-only browser auth: rejected for now in favor of Django sessions and CSRF
  protections for the Nuxt browser client.
- Store wallet addresses in a separate table immediately: deferred because the
  MVP only needs one nullable wallet address while wallet interaction rules are
  still open.
- Use reCAPTCHA v3: rejected for now because it requires score tuning and
  monitoring before Beacon has enough production traffic.

## Consequences

- Backend tests must cover password hashing, session login, generic reset
  responses, reset email delivery, and captcha failure.
- Frontend auth forms must collect and submit the expanded payloads.
- Future Google login should attach a provider identity to the existing account.
- Product specs must still resolve reputation and account-credit semantics before
  those reserved fields are used in ranking, rewards, or governance.

## Links

- `docs/plans/0005-password-auth-and-profile-foundation.md`
- `docs/api/openapi.md`
- `docs/product/open-questions.md`
- `docs/tokenomics/rewards.md`
