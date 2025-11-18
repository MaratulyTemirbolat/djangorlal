# Python modules
from typing import Optional, Sequence

# Django modules
from django.contrib.admin import ModelAdmin, register
from django.core.handlers.wsgi import WSGIRequest

# Project modules
from apps.tasks.models import Task, UserTask, Project


@register(Project)
class ProjectAdmin(ModelAdmin):
    """
    Project admin configuration class.
    """

    list_display = (
        "id",
        "name",
        "author",
        "created_at"
    )
    list_display_links = (
        "id",
    )
    list_per_page = 50
    search_fields = (
        "id",
        "name",
    )
    ordering = (
        "-updated_at",
    )
    # list_editable = (
    #     "name",
    # )
    list_filter = (
        # "author",
        "updated_at",
    )

    # fields = (
    #     "name",
    #     "author",
    #     "users",
    # )
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    filter_horizontal = (
        "users",
    )
    save_on_top = True
    fieldsets = (
        (
            "Project Information",
            {
                "fields": (
                    "name",
                    "author",
                    "users",
                )
            }
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            }
        )
    )

    # def get_readonly_fields(self, request: WSGIRequest, obj: Optional[Project] = None) -> Sequence[str]:
    #     """Get dynamically readonly fields."""
    #     if obj:
    #         return self.readonly_fields + ("author", "name", "users")
    #     return self.readonly_fields

    def has_add_permission(self, request: WSGIRequest) -> bool:
        """Disable add permission."""
        return True

    def has_delete_permission(self, request: WSGIRequest, obj: Optional[Project] = None) -> bool:
        """Disable delete permission."""
        return False

    def has_change_permission(self, request: WSGIRequest, obj: Optional[Project] = None) -> bool:
        """Disable change permission."""
        return True

    # def has_module_permission(self, request: WSGIRequest) -> bool:
    #     """Disable module permission."""
    #     return False


@register(Task)
class TaskAdmin(ModelAdmin):
    """
    Task admin configuration class.
    """

    ...


@register(UserTask)
class UserTaskAdmin(ModelAdmin):
    """
    UserTask admin configuration class.
    """

    ...
