import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from notifications.services.engine import fire_trigger

from .serializers import (
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger("notifications")
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """JWT login by email. Fires the ``login`` trigger on success."""

    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get("email")
            user = User.objects.filter(email__iexact=email).first()
            if user:
                fire_trigger("login", user, {"name": user.username or user.email})
        return response


class LogoutView(APIView):
    """Fires the ``logout`` trigger. Token invalidation is client-side (discard token)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        fire_trigger(
            "logout", request.user, {"name": request.user.username or request.user.email}
        )
        return Response({"detail": "Logged out."}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
