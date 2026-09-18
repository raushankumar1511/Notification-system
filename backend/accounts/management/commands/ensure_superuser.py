import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Create an admin user from env vars if it doesn't already exist.

    Idempotent and safe to run on every deploy (e.g. from the Render build command),
    which is how we bootstrap an admin on hosts without shell access. Reads:
      DJANGO_SUPERUSER_EMAIL     (required)
      DJANGO_SUPERUSER_PASSWORD  (required)
      DJANGO_SUPERUSER_USERNAME  (optional; defaults to the email)
    If email or password are missing, it skips quietly instead of failing the build.
    """

    help = "Create a superuser from DJANGO_SUPERUSER_* env vars if absent."

    def handle(self, *args, **options):
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or email).strip()

        if not email or not password:
            self.stdout.write(
                "ensure_superuser: DJANGO_SUPERUSER_EMAIL/PASSWORD not set; skipping."
            )
            return

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(f"ensure_superuser: '{email}' already exists; skipping.")
            return

        user = User(email=email, username=username, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"ensure_superuser: created admin '{email}'."))
