# Python modules
from typing import Any

# Django REST Framework modules
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet

# Project modules
from apps.tasks.models import Project


class IsUserInProject(BasePermission):
    """
    Custom permission to check if the user is part of the project.
    """

    message = "Forbidden! You are not a member of this project."

    def has_object_permission(self, request: DRFRequest, view: ViewSet, obj: Project | int) -> bool:
        """
        Check if the user is part of the project.
        """
        project_id: Any = obj.id if isinstance(obj, Project) else obj

        if not isinstance(project_id, int):
            return False

        return Project.objects.filter(
            users__id=request.user.id,
            id=project_id
        ).exists()

    # def has_permission(self, request, view):
    #     return super().has_permission(request, view)