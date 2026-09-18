from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_staff", "last_seen")
    ordering = ("email",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Notifications", {"fields": ("phone_number", "last_seen")}),
    )
