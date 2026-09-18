# Frontend architecture

## Routing (App Router, all client components)
- `/` landing · `/login` · `/register` · `/dashboard` (user) · `/admin` (staff).
- Route guards are client-side: pages read `useAuth()`; unauthenticated users are
  redirected to `/login`, non-staff away from `/admin`.

## State & auth
- `AuthProvider` (`lib/auth.tsx`) loads the current user from `/api/auth/me/` on mount
  (if a token exists) and exposes `user`, `login`, `logout`, `refreshUser`.
- Tokens (`access`, `refresh`) live in `localStorage` (wrapped for SSR/private mode).
- `lib/api.ts` attaches `Authorization: Bearer <access>` and retries once via
  `/api/auth/refresh/` on a 401.

## Admin grid
`/admin` fetches `/api/triggers/` (triggers with nested templates) and renders a table:
rows = triggers, columns = the 3 channels. Each cell:
- empty → **+ Create** (opens `TemplateEditor`),
- present → status badge (ON/OFF) + **Edit** / **Turn on-off** (toggle) / **Test**.
`TemplateEditor` shows channel-specific fields (email subject; push title+url; WhatsApp
approved-template name/language/param map) and a variables editor. `LogsPanel` shows the
recent `NotificationLog` rows.

## Web push
`dashboard` calls `initOneSignal(user.id)` → `OneSignal.login(user.id)` so the backend
can target by External ID, and offers a subscribe button. Requires HTTPS (deployed URL).

See `COMPONENTS.md` and `INTEGRATION.md` for specifics.
