from django.core.management.base import BaseCommand

from notifications.services.scheduled import run_scheduled_triggers


class Command(BaseCommand):
    help = "Evaluate SCHEDULED triggers and notify inactive users (idempotent)."

    def handle(self, *args, **options):
        summary = run_scheduled_triggers()
        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduled run complete: {summary['total_users_notified']} "
                f"user(s) notified. Per trigger: {summary['per_trigger']}"
            )
        )
