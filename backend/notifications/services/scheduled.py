"""Evaluate SCHEDULED triggers (e.g. "not logged in for N days").

Idempotent: a user is notified at most once per inactivity episode. The ``window_key``
is the user's ``last_seen`` date, so a given episode has a stable key; when the user
returns and later goes inactive again, ``last_seen`` changes and a new notification can
fire. A SentNotification row is the dedupe guard, created atomically via get_or_create.
"""

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import SentNotification, Template, Trigger
from .engine import fire_trigger

logger = logging.getLogger("notifications")
User = get_user_model()


def run_scheduled_triggers() -> dict:
    now = timezone.now()
    triggers = Trigger.objects.filter(
        event_type=Trigger.Kind.SCHEDULED, is_active=True
    )

    total_fired = 0
    per_trigger: dict[str, int] = {}

    for trigger in triggers:
        hours = (trigger.schedule_config or {}).get("inactivity_hours")
        if not hours:
            continue
        # Only bother if this trigger has at least one enabled template.
        if not Template.objects.filter(trigger=trigger, is_enabled=True).exists():
            continue

        cutoff = now - timedelta(hours=hours)
        inactive_users = User.objects.filter(
            is_active=True, last_seen__isnull=False, last_seen__lte=cutoff
        )

        fired = 0
        for user in inactive_users:
            window_key = user.last_seen.date().isoformat()
            _, created = SentNotification.objects.get_or_create(
                user=user, trigger=trigger, window_key=window_key
            )
            if not created:
                continue  # already notified for this inactivity episode
            logs = fire_trigger(
                trigger.slug,
                user,
                {"name": user.username or user.email},
            )
            if logs:
                fired += 1

        per_trigger[trigger.slug] = fired
        total_fired += fired
        logger.info("scheduled '%s': notified %d user(s)", trigger.slug, fired)

    return {"total_users_notified": total_fired, "per_trigger": per_trigger}
