# Progress

Status of each build-order step. Update as work completes.
Legend: ✅ done · 🚧 in progress · ⬜ planned

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Scaffold monorepo (Django, Next.js, Docker Postgres, docs skeleton) | ✅ | venv, deps, `docker-compose.yml` (port 5433) |
| 2 | Models + migrations + `seed_triggers` | ✅ | User, Trigger, Template, NotificationLog, SentNotification; 6 triggers seeded |
| 3 | Auth (SimpleJWT) + CORS + `is_staff` + `last_seen` | ✅ | Custom JWT auth class stamps `last_seen` |
| 4 | Send pipeline + render + 3 provider clients | ✅ | Graceful no-key degradation |
| 5 | Firing engine + inline events + test-send | ✅ | login/logout fire inline; events endpoint |
| 6 | Admin APIs (trigger/template CRUD, toggle, test-send, logs) | ✅ | DRF viewsets, IsAdminUser |
| 7 | Scheduled command + secured endpoint + dedupe + GH Actions | ✅ | `run_scheduled_triggers`, `/api/internal/run-scheduled/` |
| 8 | Frontend user site (auth + dashboard + fire buttons) | ✅ | login/register/dashboard |
| 9 | Frontend admin grid (grid, editor, toggle, test-send, logs) | ✅ | `/admin` grid + TemplateEditor + LogsPanel |
| 10 | Web push (OneSignal init, service worker, subscribe) | ✅ | External-id login; SW in `public/` |
| 11 | Deploy configs (`render.yaml`, `.env.example`, README) | ✅ | Render blueprint + GH Actions cron |
| 12 | Documentation pass (CLAUDE.md, docs/*) | ✅ | root/backend/frontend guides |
| 13 | End-to-end test + video | 🚧 | Backend tests pass (24); local E2E verified; live deploy + video pending (user) |

## Verified so far
- 28 backend tests pass (`python manage.py test tests`) — incl. template validation.
- Frontend `npm run build` succeeds (all routes).
- Live local flow: login → create template → toggle → test-send (skipped w/o keys) →
  fire event → logs. Graceful degradation confirmed.

## Post-build refinements
- **Validation added:** backend `TemplateSerializer.validate()` enforces per-channel
  required fields (email: subject+body; webpush: title+body; whatsapp: template_name)
  and rejects duplicate cells. Frontend `TemplateEditor` mirrors this with inline field
  errors and surfaces backend validation errors. (31 backend tests pass.)
- **UI redesign:** Inter font; refined neutral (zinc) palette with near-black primary
  actions; polished nav, landing, auth, dashboard, admin grid, editor, and logs.
- **Add / delete triggers:** admin can create a new trigger row (`AddTriggerModal`,
  auto-slug from name; scheduled triggers require inactivity days) and delete a row
  (with confirm). Backend: `TriggerSerializer` auto-slug + scheduled validation.

## Remaining (user-owned)
- Create sandbox accounts + add real keys (see `backend/docs/PROVIDERS.md`).
- Deploy backend (Render) + frontend (Vercel); set env vars + the GH Actions cron
  variables; verify CORS.
- Record the narrated end-to-end walkthrough video and add all links to the README.
