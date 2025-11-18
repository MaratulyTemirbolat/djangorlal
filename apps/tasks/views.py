# Python modules
from typing import Any

# Django modules
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet, Count

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.decorators import action

# Project modules
from apps.tasks.models import Project, Task, UserTask
from apps.tasks.permissions import IsUserInProject
from apps.tasks.serializers import (
    ProjectBaseSerializer,
    ProjectListSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    TaskListSerializer,
    TaskCreateSerializer,
)

def hello_view(
    request: HttpRequest,
    *args: tuple[Any, ...],
    **kwargs: dict[str, Any]
) -> HttpResponse:
    """
    Return a simple HTML page.

    Parameters:
        request: HttpRequest
            The request object.
        *args: list
            Additional positional arguments.
        **kwargs: dict
            Additional keyword arguments.
    
    Returns:
        HttpResponse
            Rendered HTML page with a name in the context.
    """

    return render(
        request=request,
        template_name="index.html",
        context={"name": "Temirbolat", "names": []},
        status=200
    )


class ProjectViewSet(ViewSet):
    """
    ViewSet for handling Project-related endpoints.
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = ProjectBaseSerializer


    def list(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list projects.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing list of projects.
        """

        all_projects: QuerySet[Project] = Project.objects.select_related("author").annotate(
            users_count=Count("users", distinct=True)
        ).all()

        serializer: ProjectListSerializer = ProjectListSerializer(
            all_projects,
            many=True
        )

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK
        )

    def create(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle POST requests to create a new project.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating the result of the creation operation.
        """
        serializer: ProjectCreateSerializer = ProjectCreateSerializer(
            data=request.data
        )
        
        if not serializer.is_valid():
            return DRFResponse(
                data=serializer.errors,
                status=HTTP_400_BAD_REQUEST
            )
        
        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED
        )

    def partial_update(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle PATCH requests to partially update a project.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating the result of the update operation.
        """
        try:
            project: Project = Project.objects.get(id=kwargs["pk"])
        except Project.DoesNotExist:
            return DRFResponse(
                data={
                    "pk": [f"Project with id={kwargs['pk']} does not exist."]
                },
                status=HTTP_404_NOT_FOUND
            )

        serializer: ProjectUpdateSerializer = ProjectUpdateSerializer(
            data=request.data,
            instance=project,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK
        )

    def destroy(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle DELETE requests to delete a project.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating the result of the deletion operation.
        """
        try:
            project: Project = Project.objects.get(id=kwargs["pk"])
        except Project.DoesNotExist:
            return DRFResponse(
                data={
                    "pk": [f"Project with id={kwargs['pk']} does not exist."]
                },
                status=HTTP_404_NOT_FOUND
            )

        project.delete()

        return DRFResponse(
            status=HTTP_204_NO_CONTENT
        )

    @action(
        methods=("GET",),
        detail=True,
        url_name="tasks",
        url_path="tasks",
        # permission_classes=(IsAuthenticated, IsUserInProject,)
    )
    def get_tasks(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle GET requests to retrieve tasks for a specific project.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        Returns:
            DRFResponse
                A response containing list of tasks for the specified project.
        """
        try:
            project: Project = Project.objects.get(id=kwargs["pk"])
        except Project.DoesNotExist:
            return DRFResponse(
                data={
                    "id": [f"Project with id={kwargs['pk']} does not exist."]
                },
                status=HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request=request, obj=project)

        return DRFResponse(
            data=TaskListSerializer(
                project.tasks.prefetch_related("assignees").all(),
                many=True,
            ).data,
            status=HTTP_200_OK
        )

    @action(
        methods=("POST",),
        detail=True,
        url_name="create_task",
        url_path="create-task",
        permission_classes=(IsAuthenticated, IsUserInProject,),
    )
    def create_task(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle POST requests to create a new task for a specific project.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        Returns:
            DRFResponse
                A response indicating the result of the task creation operation.
        """
        try:
            project: Project = Project.objects.get(id=kwargs["pk"])
        except Project.DoesNotExist:
            return DRFResponse(
                data={
                    "id": [f"Project with id={kwargs['pk']} does not exist."]
                },
                status=HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request=request, obj=project)


        serializer: TaskCreateSerializer = TaskCreateSerializer(
            data=request.data,
            context={
                "pk": kwargs["pk"],
                "request": request,
            }
        )

        serializer.is_valid(raise_exception=True)

        task: Task = serializer.save()
        UserTask.objects.create(
            task_id=task.id,
            user_id=request.user.id,
        )

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED
        )


class TaskViewSet(ViewSet):
    """
    ViewSet for handling Task-related endpoints.
    """
    pass
