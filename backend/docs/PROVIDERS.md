# Providers — sandbox setup & integration notes

All three are optional at runtime: with a key missing, the send is logged as `skipped`
and nothing crashes. Add keys to `backend/.env` (see `.env.example`).

## WhatsApp — Meta WhatsApp Cloud API (sandbox)
Setup:
1. Create an app at [developers.facebook.com](https://developers.facebook.com) → add the
   **WhatsApp** product.
2. In **API Setup**, note the **temporary access token** and the **test phone number id**.
3. Add your own phone number to the **test recipient allow-list** (only listed numbers
   can receive test messages).
4. `.env`: `WHATSAPP_ACCESS_TOKEN=…`, `PHONE_NUMBER_ID=…`, `WHATSAPP_API_VERSION=v21.0`.

Integration reality (important):
- Business-initiated messages **must use a Meta-approved message template** referenced by
  `template_name` + `language_code`, with **positional** params (`{{1}}`, `{{2}}`). Free
  text is only allowed inside a 24h window opened by the *user* messaging you first — a
  website login does not open it.
- In the admin grid's WhatsApp cell, set `template_name` (e.g. the pre-approved
  `hello_world`), `language_code` (e.g. `en_US`), and `param_map` = the variable names, in
  order, that fill the template's params. The `body` field is a preview only.
- The temporary token **expires ~24h** — regenerate it in API Setup when tests start
  returning a 190/auth error.

## Email — Resend
Setup:
1. Sign up at [resend.com](https://resend.com), create an **API key**.
2. Verify a sender (a verified domain, or the onboarding sender for quick tests).
3. `.env`: `RESEND_API_KEY=…`, `RESEND_FROM_EMAIL=you@yourdomain.com`.

Notes: content is sent verbatim, so `{{var}}` rendering works fully; bodies are
HTML-escaped. Free tier ≈ 3,000 emails/month.

_Switching provider?_ Keep the same pattern (verified sender + API token) and adapt
`services/email.py`; note the provider used in the README.

## Web Push — OneSignal
Setup:
1. Sign up at [onesignal.com](https://onesignal.com), create a **Web** app; enable
   **Web Push** only (skip Android/iOS).
2. Settings → **Keys & IDs**: copy the **App ID** and the **REST API Key**.
3. Set the site URL to your frontend origin (exact scheme+host). HTTPS required — test on
   the deployed Vercel URL (localhost differs).
4. Backend `.env`: `ONESIGNAL_APP_ID=…`, `ONESIGNAL_REST_API_KEY=…`.
   Frontend `.env.local`: `NEXT_PUBLIC_ONESIGNAL_APP_ID=…`.

Notes:
- We target users by **External ID = the Django user id**. The frontend calls
  `OneSignal.login(user.id)`; the backend sends with `include_aliases.external_id`. No
  volatile subscription/player id is stored.
- The service worker must be served at the site root: `frontend/public/OneSignalSDKWorker.js`.
