# Django modules
from django.contrib.admin import ModelAdmin, register

# Project modules
from apps.tasks.models import Task, UserTask, Project


@register(Project)
class ProjectAdmin(ModelAdmin):
    """
    Project admin configuration class.
    """

    ...


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
