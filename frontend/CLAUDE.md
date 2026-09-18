@AGENTS.md

# CLAUDE.md — frontend (Next.js App Router)

> Next.js 16: `AGENTS.md` (imported above) is auto-generated and warns that APIs may
> differ from older Next. This app is client-heavy (localStorage JWT, external API), so
> it mostly uses `next/link` + `next/navigation` (`useRouter`) — both unchanged. It does
> not use server-side data fetching or the async request APIs.

## Scope
User site + admin grid. Deploys to Vercel. TypeScript + Tailwind v4.

## Layout (`src/`)
- `app/layout.tsx` — wraps everything in `AuthProvider`.
- `app/page.tsx` — landing. `app/login`, `app/register` — auth.
- `app/dashboard` — user site: fire `order_placed`/`password_reset`, enable web push.
- `app/admin` — the trigger×channel grid (staff only). Uses `TemplateEditor` + `LogsPanel`.
- `components/` — `Nav`, `TemplateEditor` (channel-specific fields incl. WhatsApp),
  `LogsPanel`.
- `lib/api.ts` — fetch wrapper: Bearer token, one auto-refresh on 401, typed calls.
- `lib/auth.tsx` — `AuthProvider` / `useAuth` (loads `/auth/me/`, login/logout).
- `lib/onesignal.ts` — init + `OneSignal.login(userId)` + subscribe.
- `lib/types.ts` — shared types (Channel, Trigger, Template, NotificationLog, User).
- `public/OneSignalSDKWorker.js` — service worker (must stay at root).

## Commands (from `frontend/`)
```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build + typecheck
```

## Conventions
- All pages are Client Components (`"use client"`) — auth state lives in React + localStorage.
- Env: `NEXT_PUBLIC_API_BASE_URL` (backend), `NEXT_PUBLIC_ONESIGNAL_APP_ID`. Both must be
  `NEXT_PUBLIC_`-prefixed to reach the browser; set them in Vercel.
- All backend calls go through `lib/api.ts` — don't scatter `fetch` calls.
- localStorage access is wrapped in try/catch (SSR/private-mode safe); keep it that way.
- Reusable classes `.input`, `.card`, `.btn-primary`, `.btn-secondary` live in
  `globals.css`.

See `docs/` for architecture, components, integration, and Vercel deploy.
