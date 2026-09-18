from django.utils.text import slugify
from rest_framework import serializers

from .models import Channel, NotificationLog, Template, Trigger


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id",
            "trigger",
            "channel",
            "is_enabled",
            "subject",
            "title",
            "body",
            "provider_config",
            "variables",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def validate(self, attrs):
        """Enforce the fields each channel actually needs before a template is saved."""
        channel = attrs.get("channel") or getattr(self.instance, "channel", None)
        if not channel:
            raise serializers.ValidationError({"channel": "This field is required."})

        def field(name):
            if name in attrs:
                return attrs.get(name)
            return getattr(self.instance, name, None) if self.instance else None

        def text(name):
            return (field(name) or "").strip() if isinstance(field(name), str) else field(name)

        errors: dict[str, str] = {}
        if channel == Channel.EMAIL:
            if not text("subject"):
                errors["subject"] = "Subject is required for email templates."
            if not text("body"):
                errors["body"] = "Body is required for email templates."
        elif channel == Channel.WEBPUSH:
            if not text("title"):
                errors["title"] = "Title is required for web push templates."
            if not text("body"):
                errors["body"] = "Body is required for web push templates."
        elif channel == Channel.WHATSAPP:
            cfg = field("provider_config") or {}
            if not str(cfg.get("template_name", "")).strip():
                errors["provider_config"] = (
                    "An approved WhatsApp template name is required."
                )

        # Prevent a duplicate cell (one template per trigger+channel).
        if self.instance is None:
            trigger = attrs.get("trigger")
            if trigger and Template.objects.filter(
                trigger=trigger, channel=channel
            ).exists():
                raise serializers.ValidationError(
                    "A template already exists for this trigger and channel; edit it instead."
                )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TriggerSerializer(serializers.ModelSerializer):
    templates = TemplateSerializer(many=True, read_only=True)

    class Meta:
        model = Trigger
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "event_type",
            "schedule_config",
            "is_active",
            "templates",
        ]
        # slug is derived from name on create; not client-editable.
        read_only_fields = ["id", "slug"]

    def validate(self, attrs):
        event_type = attrs.get("event_type") or getattr(
            self.instance, "event_type", Trigger.Kind.EVENT
        )
        if event_type == Trigger.Kind.SCHEDULED:
            cfg = attrs.get("schedule_config")
            if cfg is None and self.instance:
                cfg = self.instance.schedule_config
            hours = (cfg or {}).get("inactivity_hours")
            try:
                valid = hours is not None and int(hours) > 0
            except (TypeError, ValueError):
                valid = False
            if not valid:
                raise serializers.ValidationError(
                    {
                        "schedule_config": "Scheduled triggers need a positive "
                        "'inactivity_hours'."
                    }
                )
        return attrs

    def create(self, validated_data):
        validated_data["slug"] = self._unique_slug(validated_data.get("name", ""))
        return super().create(validated_data)

    @staticmethod
    def _unique_slug(name: str) -> str:
        base = slugify(name) or "trigger"
        slug = base
        i = 2
        while Trigger.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        return slug


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "user",
            "template",
            "trigger_slug",
            "channel",
            "recipient",
            "status",
            "is_test",
            "provider_message_id",
            "error",
            "created_at",
        ]
        read_only_fields = fields


class TestSendSerializer(serializers.Serializer):
    recipient = serializers.CharField(required=False, allow_blank=True)
    context = serializers.DictField(required=False)
