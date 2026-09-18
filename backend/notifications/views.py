import logging

from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NotificationLog, Template, Trigger
from .serializers import (
    NotificationLogSerializer,
    TemplateSerializer,
    TestSendSerializer,
    TriggerSerializer,
)
from .services.engine import fire_trigger, test_send

logger = logging.getLogger("notifications")


class TriggerViewSet(viewsets.ModelViewSet):
    """Admin CRUD for triggers (grid rows). Includes nested templates on read."""

    queryset = Trigger.objects.prefetch_related("templates").all()
    serializer_class = TriggerSerializer
    permission_classes = [permissions.IsAdminUser]


class TemplateViewSet(viewsets.ModelViewSet):
    """Admin CRUD for templates (grid cells), plus toggle and test-send."""

    queryset = Template.objects.select_related("trigger").all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        template = self.get_object()
        template.is_enabled = not template.is_enabled
        template.save(update_fields=["is_enabled"])
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="test-send")
    def test_send(self, request, pk=None):
        template = self.get_object()
        serializer = TestSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipient = serializer.validated_data.get("recipient", "")
        context = serializer.validated_data.get("context", {})
        log = test_send(template, recipient, context)
        return Response(
            {
                "status": log.status,
                "recipient": log.recipient,
                "error": log.error,
                "log": NotificationLogSerializer(log).data,
            },
            status=status.HTTP_200_OK,
        )


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Recent notification logs (admin view for the demo)."""

    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = NotificationLog.objects.all()
        channel = self.request.query_params.get("channel")
        if channel:
            qs = qs.filter(channel=channel)
        return qs[:200]


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def fire_event(request, slug: str):
    """Fire an EVENT trigger for the current user (e.g. order_placed, password_reset)."""
    context = request.data.get("context", {}) if isinstance(request.data, dict) else {}
    context.setdefault("name", request.user.username or request.user.email)
    logs = fire_trigger(slug, request.user, context)
    return Response(
        {
            "trigger": slug,
            "sent": [
                {"channel": log.channel, "status": log.status, "error": log.error}
                for log in logs
            ],
        }
    )


class RunScheduledView(APIView):
    """Secret-guarded endpoint that runs scheduled-trigger evaluation.

    Called by a free external cron (GitHub Actions). Requires the shared secret in the
    ``X-Scheduled-Secret`` header so it cannot be triggered by the public.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        secret = request.headers.get("X-Scheduled-Secret", "")
        if not secret or secret != settings.SCHEDULED_RUN_SECRET:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        from .services.scheduled import run_scheduled_triggers

        summary = run_scheduled_triggers()
        return Response({"detail": "Scheduled run complete.", **summary})
