# Notification System

Admins manage **all notifications from one screen** — no need to open WhatsApp,
the email provider, or the push provider. A single admin grid maps **triggers** (rows)
to **channels** (WhatsApp / Email / Web Push, columns); each cell is a template you can
create, edit, toggle on/off, and test-send. When a trigger fires on the site, every
enabled channel sends its rendered template to the user.

- **Backend:** Django + DRF + Postgres → Render
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind → Vercel
- **Channels:** WhatsApp Cloud API (sandbox), Resend (email), OneSignal (web push)

## Live URLs
- Frontend (Vercel): _add after deploy_
- Backend (Render): _add after deploy_
- Walkthrough video: _add link_

## Admin login
1. Create an admin user on the backend: `python manage.py createsuperuser`
   (username, email, password). Any user with `is_staff=True` can reach the admin panel.
2. Log in on the frontend at `/login` with that email + password. Staff users land on
   `/admin`.
3. The Django admin fallback UI is also available at `<backend>/admin/`.

## Triggers built (seeded by `python manage.py seed_triggers`)
| Trigger | Type | Fires when |
|---|---|---|
| `login` | EVENT | user logs in |
| `logout` | EVENT | user logs out |
| `order_placed` | EVENT | user places an order (demo button) |
| `password_reset` | EVENT | user requests a reset (demo button) |
| `inactive_1_day` | SCHEDULED | user inactive for 24h |
| `inactive_1_week` | SCHEDULED | user inactive for 7 days |

Each trigger works on all three channels once a template exists and its toggle is on.

## Run locally
```bash
# 1. Database (Docker Postgres on host port 5433)
cd backend && docker compose up -d

# 2. Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in provider keys (optional for a dry run)
python manage.py migrate
python manage.py seed_triggers
python manage.py createsuperuser
python manage.py runserver      # http://localhost:8000

# 3. Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_BASE_URL + OneSignal app id
npm run dev                         # http://localhost:3000
```
Without provider keys the app runs fine — sends are recorded as `skipped` in the logs
instead of crashing. Add keys to actually deliver messages.

## Environment variables
**Backend** (`backend/.env`, see `backend/.env.example`): `SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `SCHEDULED_RUN_SECRET`,
`WHATSAPP_ACCESS_TOKEN`, `PHONE_NUMBER_ID`, `WHATSAPP_API_VERSION`, `RESEND_API_KEY`,
`RESEND_FROM_EMAIL`, `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_KEY`.

**Frontend** (`frontend/.env.local`, see `frontend/.env.local.example`):
`NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_ONESIGNAL_APP_ID`.

## Sandbox account setup
Step-by-step for Meta WhatsApp, Resend, and OneSignal: **`backend/docs/PROVIDERS.md`**.
> The WhatsApp sandbox token expires ~24h — regenerate it in Meta for Developers when
> test sends start failing. WhatsApp business-initiated messages require a
> **Meta-approved template** (e.g. `hello_world`), not free text.

## Deploy
- Backend → Render: **`backend/docs/DEPLOY_RENDER.md`** (uses `render.yaml`).
- Frontend → Vercel: **`frontend/docs/DEPLOY_VERCEL.md`** (root directory = `frontend`).
- Scheduled triggers cron: set the `BACKEND_URL` repo variable and `SCHEDULED_RUN_SECRET`
  repo secret so `.github/workflows/scheduled-triggers.yml` can run.

## Tests
```bash
cd backend && python manage.py test tests
```

## Architecture & docs
See `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, and the per-app `docs/` folders.
