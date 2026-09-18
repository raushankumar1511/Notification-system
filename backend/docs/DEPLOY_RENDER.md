# Deploy the backend to Render

The repo root `render.yaml` is a Blueprint that provisions a free Postgres + a web
service running the Django app (`rootDir: backend`).

## Steps
1. Push the repo to GitHub.
2. Render dashboard → **New → Blueprint** → pick this repo. Render reads `render.yaml`.
3. It creates `notif-db` (Postgres) and `notif-backend` (web). `DATABASE_URL`,
   `SECRET_KEY`, and `SCHEDULED_RUN_SECRET` are wired/generated automatically.
4. Set the `sync:false` env vars in the service's **Environment** tab:
   - `ALLOWED_HOSTS` = your Render host, e.g. `notif-backend.onrender.com`
   - `CORS_ALLOWED_ORIGINS` = your Vercel URL, e.g. `https://your-app.vercel.app`
   - `WHATSAPP_ACCESS_TOKEN`, `PHONE_NUMBER_ID`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`,
     `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_KEY`
5. Deploy. Build runs `pip install`, `collectstatic`, `migrate`. Start runs gunicorn
   bound to `$PORT`. Health check: `/health/`.
6. Seed triggers once (Render **Shell** tab): `python manage.py seed_triggers` and
   `python manage.py createsuperuser`.

## Notes
- `RENDER_EXTERNAL_HOSTNAME` is auto-added to `ALLOWED_HOSTS` in `settings.py`, but set
  `ALLOWED_HOSTS` explicitly too.
- Free web services spin down when idle (~15 min) → first request is slow. The GitHub
  Actions cron both runs scheduled triggers and keeps the service warm. Warm it before
  recording the demo video.
- Scheduled triggers: set the GitHub repo **variable** `BACKEND_URL` to the Render URL and
  the repo **secret** `SCHEDULED_RUN_SECRET` to match the service's value (see
  `.github/workflows/scheduled-triggers.yml`).
