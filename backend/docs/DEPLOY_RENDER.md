# Deploy the backend to Render

The repo root `render.yaml` is a Blueprint that provisions a free Postgres + a web
service running the Django app (`rootDir: backend`).

## Steps
1. Push the repo to GitHub.
2. Render dashboard → **New → Blueprint** → pick this repo. Render reads `render.yaml`.
3. It creates `notif-db` (Postgres) and `notif-backend` (web). `DATABASE_URL`,
   `SECRET_KEY`, and `SCHEDULED_RUN_SECRET` are wired/generated automatically.
4. Set the `sync:false` env vars in the service's **Environment** tab:
   - `ALLOWED_HOSTS` = `.onrender.com` (leading-dot wildcard — matches any Render host)
   - `CORS_ALLOWED_ORIGINS` = your Vercel URL, e.g. `https://your-app.vercel.app`
     (a trailing slash is tolerated)
   - **Admin bootstrap** (so no shell is needed): `DJANGO_SUPERUSER_EMAIL`,
     `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`
   - `WHATSAPP_ACCESS_TOKEN`, `PHONE_NUMBER_ID`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`,
     `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_KEY`
5. Deploy. The build runs `pip install`, `collectstatic`, `migrate`, then
   **`seed_triggers`** (creates the 6 default triggers) and **`ensure_superuser`**
   (creates the admin from the `DJANGO_SUPERUSER_*` vars). Both are idempotent, so they
   run safely on every deploy. Start runs gunicorn bound to `$PORT`; health: `/health/`.
6. **No Shell needed.** If you set the `DJANGO_SUPERUSER_*` vars *after* the first deploy,
   trigger one more deploy (**Manual Deploy → Deploy latest commit**) so the admin is
   created. Log in on the frontend with those credentials.

## Notes
- `RENDER_EXTERNAL_HOSTNAME` is auto-added to `ALLOWED_HOSTS` in `settings.py`, but set
  `ALLOWED_HOSTS` explicitly too.
- Free web services spin down when idle (~15 min) → first request is slow. The GitHub
  Actions cron both runs scheduled triggers and keeps the service warm. Warm it before
  recording the demo video.
- Scheduled triggers: set the GitHub repo **variable** `BACKEND_URL` to the Render URL and
  the repo **secret** `SCHEDULED_RUN_SECRET` to match the service's value (see
  `.github/workflows/scheduled-triggers.yml`).
