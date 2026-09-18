# CLAUDE.md — backend (Django + DRF)

## Scope
The API + notification engine. Deploys to Render. Python 3.12, venv in `venv/`.

## Layout
- `config/` — project settings (JWT, CORS, env-driven provider keys), URLs, wsgi.
- `accounts/` — custom `User` (email login, `phone_number`, `last_seen`), JWT auth
  (`authentication.py` stamps `last_seen`), auth views/serializers, `middleware.py`.
- `notifications/`
  - `models.py` — Trigger, Template, NotificationLog, SentNotification, `Channel`.
  - `views.py` — Trigger/Template/Log viewsets, `fire_event`, `RunScheduledView`.
  - `serializers.py`, `admin.py`.
  - `services/` — `send.py` (the one send pipeline), `engine.py` (`fire_trigger`,
    `test_send`), `render.py` (safe `{{var}}`), `scheduled.py`, and provider clients
    `whatsapp.py` / `email.py` / `webpush.py` (all return a `SendResult` from `base.py`).
  - `management/commands/` — `seed_triggers`, `run_scheduled_triggers`.
- `tests/` — `test_render`, `test_engine`, `test_scheduled`, `test_api`.
- `docs/` — `DATA_MODEL.md`, `API.md`, `PROVIDERS.md`, `DEPLOY_RENDER.md`.

## Common commands (from `backend/`)
```bash
docker compose up -d                       # local Postgres (host port 5433)
./venv/bin/python manage.py migrate
./venv/bin/python manage.py seed_triggers
./venv/bin/python manage.py createsuperuser
./venv/bin/python manage.py runserver      # :8000
./venv/bin/python manage.py test tests     # run the suite
./venv/bin/python manage.py run_scheduled_triggers   # evaluate scheduled triggers
```

## Conventions & invariants
- **Providers never raise** for expected failures. Missing keys → `SendResult.skipped`,
  provider errors → `SendResult.failed`. The pipeline turns these into a NotificationLog.
- **One send path:** everything goes through `services/send.py::send_template`. Real
  fires call it via `engine.fire_trigger`; test sends via `engine.test_send`.
- **Rendering:** `services/render.py` only (whitelisted `{{var}}`; email bodies are
  HTML-escaped). Never use `str.format` on user templates.
- **WhatsApp:** approved-template name + `param_map` (positional). See `docs/PROVIDERS.md`.
- **Auth:** DRF default is `IsAuthenticated`; admin viewsets use `IsAdminUser`
  (`is_staff`). `last_seen` is stamped in `accounts/authentication.py`.
- Add any new env var to `settings.py` (with a safe default) AND `.env.example`.
