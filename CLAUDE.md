# CLAUDE.md — Notification System (root)

Guide for any agent/human working in this monorepo. Keep it current.

## What this is
Admins manage all notifications from **one screen**: a grid of **triggers** (rows) ×
**channels** (WhatsApp / Email / Web Push, columns). Each cell is a **template** with
create / edit / on-off toggle / test-send. When a trigger fires on the site, every
enabled channel sends its rendered template to the user.

## Layout
- `backend/` — Django + DRF API + notification engine (deploy: Render). See
  `backend/CLAUDE.md`.
- `frontend/` — Next.js (App Router) + TS + Tailwind: user site + admin grid
  (deploy: Vercel). See `frontend/CLAUDE.md`.
- `docs/` — `ARCHITECTURE.md` (system design), `PROGRESS.md` (planned vs done, update
  it as you finish steps), `DECISIONS.md` (why the load-bearing choices were made).
- `render.yaml` — Render blueprint for the backend.
- `.github/workflows/scheduled-triggers.yml` — free hourly cron that drives the
  "not logged in for N days" triggers by hitting a secret-guarded backend endpoint.

## Cross-service contract
- **Auth:** JWT (SimpleJWT). Frontend logs in at `POST /api/auth/login/`, stores the
  access/refresh tokens, and sends `Authorization: Bearer <access>`.
- **Admin:** gated by Django `is_staff`. Admin APIs return 403 for non-staff.
- **CORS:** backend allows the frontend origin via `CORS_ALLOWED_ORIGINS`.
- **Base URL:** frontend reads `NEXT_PUBLIC_API_BASE_URL`.
- **Web push:** OneSignal External ID == the Django user id (`OneSignal.login(user.id)`
  client-side; backend targets `include_aliases.external_id`).

## Run locally
1. Backend DB: `cd backend && docker compose up -d` (Postgres on host port **5433**).
2. Backend: `cd backend && python manage.py migrate && python manage.py seed_triggers &&
   python manage.py runserver` (venv in `backend/venv`).
3. Frontend: `cd frontend && npm install && npm run dev` (http://localhost:3000).
4. Create an admin: `cd backend && python manage.py createsuperuser`.

## Conventions
- Providers never raise for expected failures; missing keys → a `skipped`/`failed`
  `NotificationLog`, never a crash. Keep this invariant.
- One send pipeline (`backend/notifications/services/send.py`) for real fires AND test
  sends. Don't add a parallel send path.
- WhatsApp is the "special" channel: approved-template name + positional params, not
  free text. See `backend/docs/PROVIDERS.md`.
- Secrets live only in `.env` (git-ignored). Update `.env.example` when adding a var.
