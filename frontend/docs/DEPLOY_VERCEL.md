# Deploy the frontend to Vercel

## Steps
1. Push the repo to GitHub.
2. Vercel → **Add New → Project** → import the repo.
3. **Root Directory: `frontend`** (this is a monorepo). Framework preset: Next.js
   (auto-detected). Build command / output are defaults.
4. **Environment Variables:**
   - `NEXT_PUBLIC_API_BASE_URL` = your Render backend URL, e.g.
     `https://notif-backend.onrender.com` (no trailing slash)
   - `NEXT_PUBLIC_ONESIGNAL_APP_ID` = your OneSignal app id
5. Deploy. Note the production URL.

## After deploy
- Add the Vercel URL to the backend's `CORS_ALLOWED_ORIGINS` on Render (and redeploy /
  update env). For preview deploys, either add each URL or set
  `CORS_ALLOWED_ORIGIN_REGEXES=^https://.*\.vercel\.app$` on the backend.
- In OneSignal, set the site URL to the Vercel production URL (exact scheme+host) so web
  push works. Web push requires HTTPS — test on the deployed URL, not localhost.
- The service worker `public/OneSignalSDKWorker.js` is served at
  `https://<app>.vercel.app/OneSignalSDKWorker.js` automatically.
