from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from notifications.models import Channel, NotificationLog, Template, Trigger
from notifications.services import send as send_mod
from notifications.services.base import SendResult
from notifications.services.engine import fire_trigger, test_send

User = get_user_model()


class FireTriggerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u1", email="u1@example.com", password="pw", phone_number="+100"
        )
        self.trigger = Trigger.objects.create(
            slug="login", name="Login", event_type=Trigger.Kind.EVENT
        )
        self.email_t = Template.objects.create(
            trigger=self.trigger,
            channel=Channel.EMAIL,
            is_enabled=True,
            subject="Hi {{name}}",
            body="Welcome {{name}}",
        )
        self.push_t = Template.objects.create(
            trigger=self.trigger,
            channel=Channel.WEBPUSH,
            is_enabled=False,  # disabled -> must not send
            title="T",
            body="B",
        )

    def test_only_enabled_channels_fire(self):
        with mock.patch.object(
            send_mod.email_client, "send_email", return_value=SendResult.sent("mid")
        ) as m_email, mock.patch.object(
            send_mod.webpush_client, "send_webpush"
        ) as m_push:
            logs = fire_trigger("login", self.user, {"name": "Ann"})

        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].channel, Channel.EMAIL)
        self.assertEqual(logs[0].status, "sent")
        m_email.assert_called_once()
        m_push.assert_not_called()

    def test_email_rendered_and_html_escaped(self):
        with mock.patch.object(
            send_mod.email_client, "send_email", return_value=SendResult.sent("mid")
        ) as m_email:
            fire_trigger("login", self.user, {"name": "<b>Ann</b>"})
        kwargs = m_email.call_args.kwargs
        self.assertEqual(kwargs["subject"], "Hi <b>Ann</b>")  # subject not escaped
        self.assertIn("&lt;b&gt;Ann&lt;/b&gt;", kwargs["html_body"])  # body escaped

    def test_inactive_trigger_does_not_fire(self):
        self.trigger.is_active = False
        self.trigger.save()
        logs = fire_trigger("login", self.user, {})
        self.assertEqual(logs, [])

    def test_unknown_trigger_returns_empty(self):
        self.assertEqual(fire_trigger("nope", self.user, {}), [])

    def test_provider_failure_is_logged_not_raised(self):
        with mock.patch.object(
            send_mod.email_client,
            "send_email",
            return_value=SendResult.failed("boom"),
        ):
            logs = fire_trigger("login", self.user, {})
        self.assertEqual(logs[0].status, "failed")
        self.assertEqual(logs[0].error, "boom")

    def test_test_send_bypasses_toggle(self):
        # push_t is disabled; test_send must still attempt it.
        with mock.patch.object(
            send_mod.webpush_client, "send_webpush", return_value=SendResult.sent("x")
        ) as m_push:
            log = test_send(self.push_t, "override-id", {"name": "Z"})
        m_push.assert_called_once()
        self.assertTrue(log.is_test)
        self.assertEqual(log.recipient, "override-id")


class WhatsAppParamMapTests(TestCase):
    def test_param_map_positional(self):
        user = User.objects.create_user(
            username="w", email="w@example.com", password="pw", phone_number="+1555"
        )
        trigger = Trigger.objects.create(slug="login", name="Login")
        t = Template.objects.create(
            trigger=trigger,
            channel=Channel.WHATSAPP,
            is_enabled=True,
            provider_config={
                "template_name": "welcome",
                "language_code": "en_US",
                "param_map": ["name", "day"],
            },
        )
        with mock.patch.object(
            send_mod.whatsapp_client, "send_whatsapp", return_value=SendResult.sent("m")
        ) as m_wa:
            send_mod.send_template(t, {"name": "Ann", "day": "Monday"}, user=user)
        kwargs = m_wa.call_args.kwargs
        self.assertEqual(kwargs["template_name"], "welcome")
        self.assertEqual(kwargs["params"], ["Ann", "Monday"])
