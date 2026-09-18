"""The single send pipeline used by both real trigger fires and test sends.

``send_template`` renders a template for a recipient, calls the right provider client,
and writes exactly one NotificationLog row. It never raises for provider problems.
"""

import logging

from ..models import Channel, NotificationLog, Template
from . import email as email_client
from . import render as render_mod
from . import webpush as webpush_client
from . import whatsapp as whatsapp_client
from .base import SendResult

logger = logging.getLogger("notifications")


def _resolve_recipient(channel: str, user, override: str | None) -> str:
    if override:
        return override
    if user is None:
        return ""
    if channel == Channel.EMAIL:
        return user.email or ""
    if channel == Channel.WHATSAPP:
        return getattr(user, "phone_number", "") or ""
    if channel == Channel.WEBPUSH:
        # OneSignal external id == our user id.
        return str(user.id)
    return ""


def send_template(
    template: Template,
    context: dict,
    *,
    user=None,
    recipient_override: str | None = None,
    is_test: bool = False,
) -> NotificationLog:
    channel = template.channel
    recipient = _resolve_recipient(channel, user, recipient_override)

    # Merge sample variable values (from the template) under the live context so tests
    # render fully even when the caller supplies a partial context.
    merged = {**(template.variables or {}), **(context or {})}

    if channel == Channel.EMAIL:
        subject = render_mod.render(template.subject, merged)
        body = render_mod.render(template.body, merged, escape_html=True)
        result = email_client.send_email(to=recipient, subject=subject, html_body=body)
        rendered = {"subject": subject, "body": body}
    elif channel == Channel.WEBPUSH:
        title = render_mod.render(template.title, merged)
        body = render_mod.render(template.body, merged)
        url = (template.provider_config or {}).get("url", "")
        result = webpush_client.send_webpush(
            external_id=recipient, title=title, body=body, url=url
        )
        rendered = {"title": title, "body": body, "url": url}
    elif channel == Channel.WHATSAPP:
        cfg = template.provider_config or {}
        param_map = cfg.get("param_map", []) or []
        params = [str(merged.get(name, f"[{name}]")) for name in param_map]
        result = whatsapp_client.send_whatsapp(
            to=recipient,
            template_name=cfg.get("template_name", ""),
            language_code=cfg.get("language_code", "en_US"),
            params=params,
        )
        rendered = {
            "template_name": cfg.get("template_name", ""),
            "language_code": cfg.get("language_code", "en_US"),
            "params": params,
        }
    else:
        result = SendResult.failed(f"Unknown channel: {channel}")
        rendered = {}

    return _log(template, channel, recipient, result, rendered, user, is_test)


def _log(
    template: Template,
    channel: str,
    recipient: str,
    result: SendResult,
    rendered: dict,
    user,
    is_test: bool,
) -> NotificationLog:
    log = NotificationLog.objects.create(
        user=user if (user is not None and getattr(user, "pk", None)) else None,
        template=template,
        trigger_slug=template.trigger.slug if template.trigger_id else "",
        channel=channel,
        recipient=recipient,
        status=result.status,
        is_test=is_test,
        provider_message_id=result.provider_message_id,
        error=result.error,
        rendered_payload={"rendered": rendered, "provider": result.payload},
    )
    logger.info(
        "send %s/%s -> %s [%s]%s",
        log.trigger_slug,
        channel,
        recipient or "(none)",
        result.status,
        f" test" if is_test else "",
    )
    return log
