from django.core.management.base import BaseCommand

from notifications.models import Trigger

DEFAULT_TRIGGERS = [
    {
        "slug": "login",
        "name": "Login",
        "description": "User signs in on the website.",
        "event_type": Trigger.Kind.EVENT,
        "schedule_config": {},
    },
    {
        "slug": "logout",
        "name": "Logout",
        "description": "User signs out.",
        "event_type": Trigger.Kind.EVENT,
        "schedule_config": {},
    },
    {
        "slug": "order_placed",
        "name": "Order placed",
        "description": "User completes a purchase.",
        "event_type": Trigger.Kind.EVENT,
        "schedule_config": {},
    },
    {
        "slug": "password_reset",
        "name": "Password reset",
        "description": "User asks to reset their password.",
        "event_type": Trigger.Kind.EVENT,
        "schedule_config": {},
    },
    {
        "slug": "inactive_1_day",
        "name": "Not logged in for 1 day",
        "description": "User has not visited the website for 24 hours.",
        "event_type": Trigger.Kind.SCHEDULED,
        "schedule_config": {"inactivity_hours": 24},
    },
    {
        "slug": "inactive_1_week",
        "name": "Not logged in for 1 week",
        "description": "User has not visited the website for 7 days.",
        "event_type": Trigger.Kind.SCHEDULED,
        "schedule_config": {"inactivity_hours": 168},
    },
]


class Command(BaseCommand):
    help = "Seed the default set of triggers (idempotent)."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for data in DEFAULT_TRIGGERS:
            obj, was_created = Trigger.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "event_type": data["event_type"],
                    "schedule_config": data["schedule_config"],
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Triggers seeded: {created} created, {updated} updated."
            )
        )
