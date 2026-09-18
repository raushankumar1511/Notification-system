from django.utils import timezone


class LastSeenMiddleware:
    """Stamp ``last_seen`` on the authenticated user for each request.

    Django's built-in ``last_login`` only updates at login; the scheduled
    "not logged in for N days" triggers need a general activity timestamp.
    To avoid a write on every single request, we throttle to at most once per
    ~5 minutes per user.
    """

    THROTTLE_SECONDS = 300

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            now = timezone.now()
            last = user.last_seen
            if last is None or (now - last).total_seconds() > self.THROTTLE_SECONDS:
                # update_fields keeps this a narrow, cheap write.
                user.last_seen = now
                user.save(update_fields=["last_seen"])
        return response
