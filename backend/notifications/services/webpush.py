"""Web Push channel via OneSignal REST API (https://onesignal.com).

Targets users by External ID (= our user id), set client-side via
``OneSignal.login(userId)``. This avoids storing volatile subscription/player ids.
Content is plain text, so ``{{var}}`` rendering (done by the caller) works fully.
"""

import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger("notifications")

ONESIGNAL_ENDPOINT = "https://api.onesignal.com/notifications"


def send_webpush(
    *, external_id: str, title: str, body: str, url: str = ""
) -> SendResult:
    if not settings.ONESIGNAL_APP_ID or not settings.ONESIGNAL_REST_API_KEY:
        msg = "OneSignal not configured (ONESIGNAL_APP_ID / ONESIGNAL_REST_API_KEY missing)."
        logger.warning(msg)
        return SendResult.skipped(msg)
    if not external_id:
        return SendResult.failed("No web-push external id for recipient.")

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "include_aliases": {"external_id": [str(external_id)]},
        "target_channel": "push",
        "headings": {"en": title or "Notification"},
        "contents": {"en": body or ""},
    }
    if url:
        payload["url"] = url

    try:
        resp = requests.post(
            ONESIGNAL_ENDPOINT,
            json=payload,
            headers={
                "Authorization": f"Key {settings.ONESIGNAL_REST_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.error("OneSignal request failed: %s", exc)
        return SendResult.failed(f"Request error: {exc}")

    data = resp.json() if resp.content else {}
    if resp.status_code >= 400:
        return SendResult.failed(f"OneSignal {resp.status_code}: {resp.text[:500]}", data)
    # OneSignal returns 200 with an "errors" field when no subscriber matched.
    if data.get("errors"):
        return SendResult.failed(f"OneSignal errors: {data['errors']}", data)
    return SendResult.sent(message_id=str(data.get("id", "")), payload=data)
