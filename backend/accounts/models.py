from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user for both website users and admins.

    Admin access is controlled by the built-in ``is_staff`` flag. Login is by email
    (``username`` is kept for Django admin compatibility but email is the identifier
    used by the API).
    """

    email = models.EmailField(unique=True)
    # WhatsApp target. Must be on the sandbox test-recipient allow-list to receive.
    phone_number = models.CharField(max_length=32, blank=True, default="")
    # Updated on every authenticated request by LastSeenMiddleware. Drives the
    # "not logged in for N days" scheduled triggers.
    last_seen = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email or self.username
