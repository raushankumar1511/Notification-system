# Decisions

Short log of load-bearing choices and why.

- **Django + DRF, Next.js, Postgres** — matches the assignment (Django on Render,
  frontend on Vercel). Next.js is the cleanest Vercel fit and makes the OneSignal
  service worker + admin UI straightforward.
- **JWT (SimpleJWT), not sessions** — the Vercel↔Render split is cross-site; session
  cookies would need `SameSite=None; Secure` + CSRF plumbing. Bearer tokens avoid that.
  Admin = `is_staff`; Django `/admin` kept as a fallback.
- **Resend for email** — 3,000/mo free (vs Postmark ~100/mo), simple API, enough for
  repeated testing. Any provider works via the same pattern.
- **OneSignal for web push, targeted by External ID** — `OneSignal.login(user.id)` maps
  external_id = our user id, so the backend targets `include_aliases.external_id` and we
  never store volatile subscription/player ids. Raw REST (not the SDK) for stability.
- **WhatsApp = approved templates + positional params** — Cloud API forbids free-text
  business-initiated messages; they must reference a Meta-approved template. So the
  WhatsApp cell stores `template_name`/`language_code`/`param_map`; its body is preview
  only.
- **Scheduled triggers via GitHub Actions cron, not Render cron/Celery** — Render cron
  jobs are paid and free web services spin down; Celery needs an always-on worker + Redis.
  A free hourly GitHub Actions workflow POSTs to a secret-guarded endpoint (and keeps the
  service warm). Idempotency via `SentNotification`.
- **`last_seen` via custom JWT auth class** — DRF authenticates at the view layer, so a
  plain Django middleware sees only `AnonymousUser` on API calls. Stamping in the auth
  class captures activity for the inactivity triggers.
- **Local Postgres in Docker (host port 5433)** — isolated/disposable, matches Render's
  Postgres; 5432 was already taken locally. Prod uses Render's managed Postgres; both via
  `DATABASE_URL`.
- **Single send pipeline for real + test sends** — one code path, one place for
  rendering/escaping/logging, so behavior can't drift between the two.
