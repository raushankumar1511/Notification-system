from django.conf import settings
from django.db import models


class Channel(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "Email"
    WEBPUSH = "webpush", "Web Push"


class Trigger(models.Model):
    """An event or condition on the website that should cause notifications.

    EVENT triggers fire inline when something happens (login, logout, order placed).
    SCHEDULED triggers are evaluated periodically against user activity
    (e.g. "not logged in for 1 week"); their parameters live in ``schedule_config``.
    """

    class Kind(models.TextChoices):
        EVENT = "EVENT", "Event"
        SCHEDULED = "SCHEDULED", "Scheduled"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    event_type = models.CharField(
        max_length=10, choices=Kind.choices, default=Kind.EVENT
    )
    # For SCHEDULED triggers, e.g. {"inactivity_hours": 168} for "1 week".
    schedule_config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class Template(models.Model):
    """One grid cell: the message for a given trigger on a given channel.

    ``is_enabled`` is the on/off toggle shown in the admin grid. ``body`` (and, per
    channel, ``subject``/``title``) may contain ``{{variable}}`` placeholders rendered
    at send time. ``provider_config`` holds channel-specific settings, notably the
    WhatsApp approved-template name/language/param-map (WhatsApp cannot send free text
    for business-initiated messages). ``variables`` maps placeholder name -> sample
    value, used for UI hints and test-send defaults.
    """

    trigger = models.ForeignKey(
        Trigger, on_delete=models.CASCADE, related_name="templates"
    )
    channel = models.CharField(max_length=16, choices=Channel.choices)
    is_enabled = models.BooleanField(default=False)

    subject = models.CharField(max_length=255, blank=True, default="")  # email
    title = models.CharField(max_length=255, blank=True, default="")  # push
    body = models.TextField(blank=True, default="")

    # e.g. {"template_name": "hello_world", "language_code": "en_US",
    #       "param_map": ["name"], "url": "https://..."}
    provider_config = models.JSONField(default=dict, blank=True)
    variables = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trigger", "channel"], name="uniq_template_per_cell"
            )
        ]
        ordering = ["trigger_id", "channel"]

    def __str__(self) -> str:
        return f"{self.trigger.slug}/{self.channel}"


class NotificationLog(models.Model):
    """A record of one attempted send on one channel."""

    class Status(models.TextChoices):
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_logs",
    )
    template = models.ForeignKey(
        Template, on_delete=models.SET_NULL, null=True, blank=True
    )
    trigger_slug = models.CharField(max_length=60, blank=True, default="")
    channel = models.CharField(max_length=16, choices=Channel.choices)
    recipient = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=10, choices=Status.choices)
    is_test = models.BooleanField(default=False)
    provider_message_id = models.CharField(max_length=255, blank=True, default="")
    error = models.TextField(blank=True, default="")
    rendered_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.channel} {self.status} -> {self.recipient}"


class SentNotification(models.Model):
    """Idempotency guard for SCHEDULED triggers.

    Ensures a user is notified at most once per (trigger, window). ``window_key`` is a
    stable string for the inactivity window, e.g. the date the window opened.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_marks"
    )
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE)
    window_key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "trigger", "window_key"],
                name="uniq_sent_per_window",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id}/{self.trigger.slug}/{self.window_key}"
