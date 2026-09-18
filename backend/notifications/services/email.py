"""Email channel via Resend (https://resend.com).

Content is sent verbatim, so ``{{var}}`` rendering (done by the caller) works fully.
Missing keys -> skipped, not a crash.
"""

import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger("notifications")

RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_email(*, to: str, subject: str, html_body: str) -> SendResult:
    if not settings.RESEND_API_KEY or not settings.RESEND_FROM_EMAIL:
        msg = "Resend not configured (RESEND_API_KEY / RESEND_FROM_EMAIL missing)."
        logger.warning(msg)
        return SendResult.skipped(msg)
    if not to:
        return SendResult.failed("No recipient email address.")

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to],
        "subject": subject or "(no subject)",
        "html": html_body or "",
    }
    try:
        resp = requests.post(
            RESEND_ENDPOINT,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.error("Resend request failed: %s", exc)
        return SendResult.failed(f"Request error: {exc}")

    if resp.status_code >= 400:
        return SendResult.failed(
            f"Resend {resp.status_code}: {resp.text[:500]}",
            payload={"request": {"to": to, "subject": subject}},
        )
    data = resp.json() if resp.content else {}
    return SendResult.sent(message_id=str(data.get("id", "")), payload=data)
