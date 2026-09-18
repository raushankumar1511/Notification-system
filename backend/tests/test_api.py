from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from notifications.models import Channel, Template, Trigger
from notifications.services import send as send_mod
from notifications.services.base import SendResult

User = get_user_model()


class ApiAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", email="admin@example.com", password="pw123456",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="joe", email="joe@example.com", password="pw123456"
        )
        self.trigger = Trigger.objects.create(slug="login", name="Login")
        self.template = Template.objects.create(
            trigger=self.trigger, channel=Channel.EMAIL, is_enabled=True,
            subject="s", body="b",
        )

    def _token(self, email, password):
        resp = self.client.post(
            "/api/auth/login/", {"email": email, "password": password}, format="json"
        )
        return resp

    def test_login_returns_token_and_user(self):
        with mock.patch.object(send_mod.email_client, "send_email",
                               return_value=SendResult.sent("m")):
            resp = self._token("joe@example.com", "pw123456")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertEqual(resp.data["user"]["email"], "joe@example.com")

    def test_non_admin_cannot_list_triggers(self):
        token = self._token("joe@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get("/api/triggers/")
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_list_triggers_with_templates(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get("/api/triggers/")
        self.assertEqual(resp.status_code, 200)
        slugs = [t["slug"] for t in resp.data]
        self.assertIn("login", slugs)
        login_row = next(t for t in resp.data if t["slug"] == "login")
        self.assertEqual(len(login_row["templates"]), 1)

    def test_toggle_flips_enabled(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(f"/api/templates/{self.template.id}/toggle/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_enabled"])

    def test_empty_email_template_rejected(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(
            "/api/templates/",
            {"trigger": self.trigger.id, "channel": "webpush"},  # no title/body
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("title", resp.data)

    def test_whatsapp_requires_template_name(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(
            "/api/templates/",
            {"trigger": self.trigger.id, "channel": "whatsapp", "body": "hi"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("provider_config", resp.data)

    def test_duplicate_cell_rejected(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        # self.template already occupies (login, email)
        resp = self.client.post(
            "/api/templates/",
            {"trigger": self.trigger.id, "channel": "email", "subject": "s", "body": "b"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_valid_email_template_accepted(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        other = Trigger.objects.create(slug="logout", name="Logout")
        resp = self.client.post(
            "/api/templates/",
            {"trigger": other.id, "channel": "email", "subject": "Hi", "body": "Bye"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

    def test_create_trigger_autoslug(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(
            "/api/triggers/",
            {"name": "Cart Abandoned", "event_type": "EVENT"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["slug"], "cart-abandoned")

    def test_create_scheduled_trigger_requires_hours(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        bad = self.client.post(
            "/api/triggers/",
            {"name": "Idle", "event_type": "SCHEDULED"},
            format="json",
        )
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post(
            "/api/triggers/",
            {
                "name": "Idle 3 days",
                "event_type": "SCHEDULED",
                "schedule_config": {"inactivity_hours": 72},
            },
            format="json",
        )
        self.assertEqual(ok.status_code, 201)

    def test_delete_trigger(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.delete(f"/api/triggers/{self.trigger.id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Trigger.objects.filter(id=self.trigger.id).exists())

    def test_test_send_uses_pipeline(self):
        token = self._token("admin@example.com", "pw123456").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        with mock.patch.object(send_mod.email_client, "send_email",
                               return_value=SendResult.sent("mid")) as m_email:
            resp = self.client.post(
                f"/api/templates/{self.template.id}/test-send/",
                {"recipient": "x@example.com", "context": {"name": "Zed"}},
                format="json",
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "sent")
        m_email.assert_called_once()


class RunScheduledEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_requires_secret(self):
        resp = self.client.post("/api/internal/run-scheduled/")
        self.assertEqual(resp.status_code, 403)

    def test_runs_with_secret(self):
        resp = self.client.post(
            "/api/internal/run-scheduled/",
            **{"HTTP_X_SCHEDULED_SECRET": "dev-scheduled-secret"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("total_users_notified", resp.data)
