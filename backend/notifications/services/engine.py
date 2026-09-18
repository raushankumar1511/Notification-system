"""Trigger firing engine.

``fire_trigger`` resolves a trigger's enabled templates and dispatches each through the
send pipeline. Used for real event fires. ``test_send`` reuses the same pipeline for a
single channel, bypassing the enabled toggle.
"""

import logging

from ..models import NotificationLog, Template, Trigger

logger = logging.getLogger("notifications")


def fire_trigger(trigger_slug: str, user, context: dict | None = None) -> list[NotificationLog]:
    """Fire all enabled channels for ``trigger_slug`` to ``user``.

    Returns the NotificationLog rows created (empty if the trigger is inactive or
    missing). Never raises for provider issues.
    """
    from . import send as send_mod

    context = context or {}
    try:
        trigger = Trigger.objects.get(slug=trigger_slug)
    except Trigger.DoesNotExist:
        logger.warning("fire_trigger: unknown trigger '%s'", trigger_slug)
        return []

    if not trigger.is_active:
        logger.info("fire_trigger: trigger '%s' is inactive; skipping", trigger_slug)
        return []

    templates = Template.objects.filter(trigger=trigger, is_enabled=True)
    logs: list[NotificationLog] = []
    for template in templates:
        logs.append(send_mod.send_template(template, context, user=user))
    return logs


def test_send(template: Template, recipient: str, context: dict | None = None) -> NotificationLog:
    """Send one template to a manual recipient, ignoring the enabled toggle."""
    from . import send as send_mod

    return send_mod.send_template(
        template,
        context or {},
        recipient_override=recipient,
        is_test=True,
    )
