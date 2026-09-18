from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication

THROTTLE_SECONDS = 300


def stamp_last_seen(user) -> None:
    """Update ``last_seen`` at most once per THROTTLE_SECONDS per user."""
    if user is None or not user.is_authenticated:
        return
    now = timezone.now()
    last = getattr(user, "last_seen", None)
    if last is None or (now - last).total_seconds() > THROTTLE_SECONDS:
        user.last_seen = now
        user.save(update_fields=["last_seen"])


class LastSeenJWTAuthentication(JWTAuthentication):
    """JWT auth that also records general user activity for scheduled triggers.

    DRF authenticates at the view layer, so a plain Django middleware never sees the
    JWT-authenticated user. Stamping here captures activity on every authenticated
    API request that carries a valid Bearer token.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, _token = result
            stamp_last_seen(user)
        return result
