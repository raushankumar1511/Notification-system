"""WhatsApp channel via Meta WhatsApp Cloud API.

IMPORTANT: business-initiated messages (which every trigger is) must use a
Meta-APPROVED message template referenced by name + language, with POSITIONAL
parameters ({{1}}, {{2}}, ...). Free text is only allowed inside a 24h window opened by
the user messaging the business first, which a website login does not do.

So the template's ``provider_config`` supplies:
    template_name: str        e.g. "hello_world"
    language_code: str        e.g. "en_US"
    param_map: list[str]      variable names, in positional order, to fill {{1}}, {{2}}...

The editable ``body`` in the admin grid is a cosmetic preview only.
Missing keys / config -> skipped or failed, never a crash.
"""

import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger("notifications")


def send_whatsapp(
    *, to: str, template_name: str, language_code: str, params: list[str]
) -> SendResult:
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        msg = "WhatsApp not configured (WHATSAPP_ACCESS_TOKEN / PHONE_NUMBER_ID missing)."
        logger.warning(msg)
        return SendResult.skipped(msg)
    if not to:
        return SendResult.failed("No recipient phone number.")
    if not template_name:
        return SendResult.failed(
            "WhatsApp needs an approved template_name in provider_config."
        )

    components = []
    if params:
        components = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in params],
            }
        ]

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code or "en_US"},
            "components": components,
        },
    }
    endpoint = (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
        f"/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.error("WhatsApp request failed: %s", exc)
        return SendResult.failed(f"Request error: {exc}")

    data = resp.json() if resp.content else {}
    if resp.status_code >= 400:
        # Common: expired token (190) or number not on the test allow-list.
        return SendResult.failed(f"WhatsApp {resp.status_code}: {resp.text[:500]}", data)
    message_id = ""
    if isinstance(data.get("messages"), list) and data["messages"]:
        message_id = data["messages"][0].get("id", "")
    return SendResult.sent(message_id=message_id, payload=data)
