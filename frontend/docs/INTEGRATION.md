# Integration (auth, API, OneSignal)

## API client (`lib/api.ts`)
- Base URL: `NEXT_PUBLIC_API_BASE_URL` (trailing slash trimmed).
- Every call attaches `Authorization: Bearer <access>` when a token is stored.
- On a `401`, it tries `/api/auth/refresh/` once with the stored refresh token, then
  retries the original request.
- Throws `ApiError(status, message, data)` on failure; UI shows `err.message`.
- Exposes: `login`, `register`, `logout`, `me`, `fireEvent`, `listTriggers`,
  `createTrigger`, `createTemplate`, `updateTemplate`, `toggleTemplate`, `testSend`,
  `listLogs`.

## Auth flow
1. `login(email, password)` → stores `access`+`refresh`, returns the user.
2. `AuthProvider` keeps `user` in context; `useAuth()` everywhere.
3. `logout()` calls `/api/auth/logout/` (fires the logout trigger) then clears tokens.

## OneSignal (`lib/onesignal.ts`)
- `initOneSignal(userId)` — inits the SDK with `NEXT_PUBLIC_ONESIGNAL_APP_ID` and calls
  `OneSignal.login(String(userId))` so external_id = the Django user id. Idempotent.
- `subscribeWebPush()` — requests notification permission.
- Requires HTTPS (deployed URL); the service worker is `public/OneSignalSDKWorker.js`.
- No subscription id is sent to the backend — targeting is by external id.

## Env vars
`NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_ONESIGNAL_APP_ID` (see `.env.local.example`).
Both are build-time public vars; set them in Vercel for the deployed app.
