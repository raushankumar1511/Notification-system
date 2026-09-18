"use client";

import OneSignal from "react-onesignal";

let initialized = false;

/**
 * Initialize OneSignal once and log in the current user so the backend can target
 * web-push by External ID (= our user id). No volatile subscription id is stored.
 *
 * Requires NEXT_PUBLIC_ONESIGNAL_APP_ID and the service worker file at the site root
 * (public/OneSignalSDKWorker.js). Web push only works over HTTPS (test on the deployed
 * URL; localhost behaves differently).
 */
export async function initOneSignal(userId: number | string): Promise<void> {
  const appId = process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID;
  if (!appId) {
    console.warn("OneSignal app id not configured; web push disabled.");
    return;
  }
  if (!initialized) {
    await OneSignal.init({
      appId,
      allowLocalhostAsSecureOrigin: true,
      serviceWorkerParam: { scope: "/" },
      serviceWorkerPath: "OneSignalSDKWorker.js",
    });
    initialized = true;
  }
  await OneSignal.login(String(userId));
}

/** Prompt the browser to subscribe to web push. */
export async function subscribeWebPush(): Promise<void> {
  try {
    await OneSignal.Notifications.requestPermission();
  } catch (err) {
    console.error("Web push subscribe failed:", err);
    throw err;
  }
}

export function isPushSupported(): boolean {
  return typeof window !== "undefined" && "Notification" in window;
}
