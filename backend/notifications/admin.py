from django.contrib import admin

from .models import NotificationLog, SentNotification, Template, Trigger


class TemplateInline(admin.TabularInline):
    model = Template
    extra = 0


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "event_type", "is_active")
    list_filter = ("event_type", "is_active")
    search_fields = ("name", "slug")
    inlines = [TemplateInline]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("trigger", "channel", "is_enabled", "updated_at")
    list_filter = ("channel", "is_enabled")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "trigger_slug",
        "channel",
        "recipient",
        "status",
        "is_test",
    )
    list_filter = ("channel", "status", "is_test")
    search_fields = ("recipient", "trigger_slug")


@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "trigger", "window_key", "created_at")
