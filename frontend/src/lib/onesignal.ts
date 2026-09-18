"use client";

import OneSignal from "react-onesignal";

let initialized = false;

const APP_ID = process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID;

/** True when the OneSignal app id is present in this build. */
export function isConfigured(): boolean {
  return !!APP_ID;
}

/**
 * Initialize OneSignal once and log in the current user so the backend can target
 * web-push by External ID (= our user id). Returns whether initialization happened.
 *
 * Requires NEXT_PUBLIC_ONESIGNAL_APP_ID and the service worker file at the site root
 * (public/OneSignalSDKWorker.js). Web push only works over HTTPS.
 */
export async function initOneSignal(userId: number | string): Promise<boolean> {
  if (!APP_ID) {
    console.warn("OneSignal app id not configured; web push disabled.");
    return false;
  }
  if (!initialized) {
    await OneSignal.init({
      appId: APP_ID,
      allowLocalhostAsSecureOrigin: true,
      serviceWorkerParam: { scope: "/" },
      serviceWorkerPath: "OneSignalSDKWorker.js",
    });
    initialized = true;
  }
  await OneSignal.login(String(userId));
  return true;
}

/**
 * Prompt the browser to subscribe to web push. Returns true if permission is granted.
 * Throws if OneSignal isn't configured for this deployment.
 */
export async function subscribeWebPush(): Promise<boolean> {
  if (!APP_ID) {
    throw new Error(
      "Web push is not configured on this deployment (NEXT_PUBLIC_ONESIGNAL_APP_ID is missing).",
    );
  }
  if (!initialized) {
    throw new Error(
      "OneSignal is still initializing — reload the page and try again.",
    );
  }
  await OneSignal.Notifications.requestPermission();
  return !!OneSignal.Notifications.permission;
}

export function isPushSupported(): boolean {
  return typeof window !== "undefined" && "Notification" in window;
}
