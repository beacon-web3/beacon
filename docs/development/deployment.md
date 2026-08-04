# Deployment Environment Variable Checklist

This page is the production checklist for environment variables across the
Beacon backend and frontend. It pairs with plan
`docs/plans/0015-mvp-free-hosting-setup.md` (MVP free hosting setup).

The MVP target stack is:

- **Frontend**: Nuxt on Vercel Hobby
- **Backend**: Django on Vercel Hobby through Vercel Services, sharing one
  project and domain with the frontend (`/api/*` rewrites to the Django service)
- **PostgreSQL**: Neon free tier

## Ground Rule

Secrets go into the hosting provider's dashboard (or a secret manager), never
into committed files, images, or logs. Public variables may appear in frontend
build configuration because they are sent to browsers, but backend secrets must
stay out of the repository and out of the Nuxt runtime.

## Backend Checklist (Django)

Set these in the Vercel project settings for the Django service. The list follows
the variables declared in `apps/api/.env.example` and `apps/api/beacon_api/settings.py`.

| Variable | Value (production) | Secret? |
|---|---|---|
| `DJANGO_SECRET_KEY` | Long random value, generated per environment | Yes |
| `DJANGO_DEBUG` | `false` | No |
| `ALLOWED_HOSTS` | Vercel deployment domain, e.g. `beacon.vercel.app` | No |
| `DATABASE_URL` | Neon pooled connection string | Yes |
| `CORS_ALLOWED_ORIGINS` | Frontend origin(s), e.g. `https://beacon.vercel.app` | No |
| `CSRF_TRUSTED_ORIGINS` | Same frontend origin(s) as CORS | No |
| `FRONTEND_BASE_URL` | Frontend origin, e.g. `https://beacon.vercel.app` | No |
| `SESSION_COOKIE_SECURE` | `true` | No |
| `CSRF_COOKIE_SECURE` | `true` | No |
| `SECURE_SSL_REDIRECT` | `true` | No |
| `SECURE_HSTS_SECONDS` | `31536000` (1 year) once HTTPS is verified | No |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `true` | No |
| `SECURE_HSTS_PRELOAD` | `true` only when committing to HSTS preload | No |
| `CAPTCHA_ENABLED` | `true` before public traffic | No |
| `CAPTCHA_SECRET` | Shared secret for Cap proof-of-work captcha JWT signing (same value as frontend) | Yes |
| `EMAIL_BACKEND` | SMTP backend, e.g. `django.core.mail.backends.smtp.EmailBackend` | No |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | Resend SMTP: host `smtp.resend.com`, port `465` (SSL) or `587` (TLS); user and password are both the Resend API key | Yes (user/password) |
| `DEFAULT_FROM_EMAIL` | Verified sender, e.g. `no-reply@beacon.example` | No |
| SMTP provider variables | Provider-specific (host, port, user, password), per provider docs | Yes |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | No (public by design) |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `GOOGLE_OAUTH_REDIRECT_URI` | API redirect URI registered in Google Console | No |
| `EMAIL_VERIFICATION_MAX_ATTEMPTS` | `5` (default) | No |
| `AUTH_*_THROTTLE_RATE` | Keep defaults unless tuned | No |

Notes:

- `DJANGO_DEBUG=false` makes Django require `DJANGO_SECRET_KEY`, enforce
  `ALLOWED_HOSTS`, and use the SMTP email backend instead of the console
  backend. See `apps/api/README.md` for the full auth configuration.
- HSTS and secure-cookie settings only take effect over HTTPS. Verify the Vercel
  URL is HTTPS before enabling them.
- Frontend and backend share one Vercel domain, so browser API requests are
  same-site. `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` can use the
  deployment domain, and session cookies flow without cross-site handling.
- Vercel runs `collectstatic` during build but not migrations. Run
  `python manage.py migrate` once against the Neon database after deploying.
- Use the Neon pooled connection string; Neon compute scales to zero after idle
  and reconnects on demand.
- Vercel Hobby pauses when free-tier usage is exceeded rather than billing; the
  plan is not charged on demand.
- Do not reuse the local `.env.example` values in production.

## Frontend Checklist (Nuxt)

Set these in the Vercel project settings:

| Variable | Value (production) | Secret? |
|---|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | Same Vercel domain, e.g. `https://beacon.vercel.app` (`/api/*` rewrites to Django) | No |
| `NUXT_CAPTCHA_SECRET` | Shared secret for Cap proof-of-work captcha JWT signing (same value as backend) | Yes |

`NUXT_PUBLIC_*` variables are embedded in the browser bundle, so they must not
contain secrets. `NUXT_PUBLIC_API_BASE_URL` drives the shared `useApiFetch()`
transport in `apps/web/`; the Nuxt server reads `NUXT_CAPTCHA_SECRET` to sign Cap
proof-of-work captcha tokens.

## Verification

1. Every variable above is set in the provider dashboards, with secrets entered
   as secret values (never in code or committed `.env` files).
2. `GET https://<deployment-domain>/api/health/` returns `200 OK` with
   `{"status": "ok"}` without authentication.
3. The frontend build succeeds with `NUXT_PUBLIC_API_BASE_URL` pointing at the
   deployed API.
4. Signup, login, password reset, email verification, and Google social auth
   all work end to end from the deployed frontend.
