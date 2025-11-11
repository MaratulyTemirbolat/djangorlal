# Django modules
from django.contrib.admin import register, ModelAdmin

# Project modules
from apps.auths.models import CustomUser


@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    """Admin model for CustomUser."""

    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "full_name")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("email",)


