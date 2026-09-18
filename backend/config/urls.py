from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import LoginView, LogoutView, MeView, RegisterView
from notifications.views import (
    NotificationLogViewSet,
    RunScheduledView,
    TemplateViewSet,
    TriggerViewSet,
    fire_event,
)

router = DefaultRouter()
router.register(r"triggers", TriggerViewSet, basename="trigger")
router.register(r"templates", TemplateViewSet, basename="template")
router.register(r"logs", NotificationLogViewSet, basename="log")


def health(_request):
    return JsonResponse({"status": "ok"})


api_patterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    # Events + scheduled runner
    path("events/<slug:slug>/", fire_event, name="fire_event"),
    path("internal/run-scheduled/", RunScheduledView.as_view(), name="run_scheduled"),
    # Router: triggers, templates, logs
    *router.urls,
]

urlpatterns = [
    path("", health),
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/", include(api_patterns)),
]
