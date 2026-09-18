# Architecture

## Overview
```
┌────────────────────┐        JWT (Bearer)        ┌──────────────────────────┐
│  Next.js (Vercel)  │ ─────────────────────────► │   Django + DRF (Render)  │
│  - user site       │  NEXT_PUBLIC_API_BASE_URL  │   - auth / admin APIs    │
│  - admin grid      │ ◄───────────────────────── │   - firing engine        │
│  - OneSignal SDK   │        JSON / CORS         │   - provider clients     │
└─────────┬──────────┘                            └───────────┬──────────────┘
          │ web push (external_id = user.id)                  │
          ▼                                                   ▼
     OneSignal ◄───────── backend send ──────────►  WhatsApp Cloud API, Resend
                                                          │
                                          ┌───────────────┴───────────────┐
                                          │  Postgres (Docker / Render)     │
                                          └────────────────────────────────┘

GitHub Actions (hourly cron) ──X-Scheduled-Secret──► POST /api/internal/run-scheduled/
```

## Core model
- **Trigger** — an event (`EVENT`) or condition (`SCHEDULED`). `schedule_config` holds
  e.g. `{"inactivity_hours": 168}`.
- **Template** — one grid cell: `(trigger, channel)` unique. Holds `is_enabled` (toggle),
  `subject`/`title`/`body` (with `{{vars}}`), `provider_config` (channel-specific, e.g.
  WhatsApp approved-template name + `param_map`), and `variables` (sample values).
- **NotificationLog** — every send attempt (`sent`/`failed`/`skipped`), incl. `is_test`.
- **SentNotification** — idempotency guard for scheduled sends: unique
  `(user, trigger, window_key)`; `window_key` = the user's `last_seen` date.

## Firing paths
- **Event:** the relevant endpoint (login/logout/event ingest) calls
  `fire_trigger(slug, user, context)` → dispatches all enabled channels via the send
  pipeline. Inline, synchronous.
- **Scheduled:** `run_scheduled_triggers` finds users whose `last_seen` crossed a
  trigger's inactivity window and who have no `SentNotification` for that window, then
  fires and records the guard. Driven by the GitHub Actions cron hitting a
  secret-guarded endpoint (Render free tier has no free always-on scheduler).
- **Test send:** reuses the same pipeline for a single channel, bypassing `is_enabled`,
  with a manual recipient and `is_test=True`.

## Send pipeline (single source of truth)
`send_template(template, context, user=, recipient_override=, is_test=)`:
render → resolve recipient (email/phone/external_id) → call provider client →
write one `NotificationLog`. Never raises for provider problems.

## Key invariants
- Missing provider keys degrade gracefully (logged + `skipped`/`failed`), never crash.
- WhatsApp uses Meta-approved templates with positional params, not free text.
- `last_seen` is stamped by a custom JWT auth class (DRF authenticates at the view layer,
  so a plain middleware never sees the JWT user).

See `backend/docs/` for the data model, API reference, and provider details.
