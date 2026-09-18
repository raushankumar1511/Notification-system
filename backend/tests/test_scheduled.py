from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from notifications.models import Channel, SentNotification, Template, Trigger
from notifications.services import send as send_mod
from notifications.services.base import SendResult
from notifications.services.scheduled import run_scheduled_triggers

User = get_user_model()


class ScheduledDedupeTests(TestCase):
    def setUp(self):
        self.trigger = Trigger.objects.create(
            slug="inactive_1_week",
            name="Not logged in 1 week",
            event_type=Trigger.Kind.SCHEDULED,
            schedule_config={"inactivity_hours": 168},
        )
        Template.objects.create(
            trigger=self.trigger,
            channel=Channel.EMAIL,
            is_enabled=True,
            subject="Miss you",
            body="Come back {{name}}",
        )
        self.user = User.objects.create_user(
            username="i", email="i@example.com", password="pw"
        )
        # Inactive for 8 days.
        self.user.last_seen = timezone.now() - timedelta(days=8)
        self.user.save(update_fields=["last_seen"])

    def test_fires_once_then_deduped(self):
        with mock.patch.object(
            send_mod.email_client, "send_email", return_value=SendResult.sent("m")
        ) as m_email:
            first = run_scheduled_triggers()
            second = run_scheduled_triggers()

        self.assertEqual(first["total_users_notified"], 1)
        self.assertEqual(second["total_users_notified"], 0)  # deduped
        self.assertEqual(m_email.call_count, 1)
        self.assertEqual(
            SentNotification.objects.filter(user=self.user, trigger=self.trigger).count(),
            1,
        )

    def test_active_user_not_notified(self):
        self.user.last_seen = timezone.now()
        self.user.save(update_fields=["last_seen"])
        with mock.patch.object(
            send_mod.email_client, "send_email", return_value=SendResult.sent("m")
        ):
            result = run_scheduled_triggers()
        self.assertEqual(result["total_users_notified"], 0)

    def test_no_enabled_templates_skips(self):
        Template.objects.filter(trigger=self.trigger).update(is_enabled=False)
        with mock.patch.object(
            send_mod.email_client, "send_email", return_value=SendResult.sent("m")
        ) as m_email:
            run_scheduled_triggers()
        m_email.assert_not_called()
        # No dedupe rows created, so enabling later still works.
        self.assertEqual(SentNotification.objects.count(), 0)
