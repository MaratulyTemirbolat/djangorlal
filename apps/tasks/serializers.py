# Django REST Framework modules
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    Field
)

# Project modules
from apps.tasks.models import Project, Task
from apps.abstracts.serializers import CustomUserForeignSerializer


class CurrentPKURLDefault:
    """Default value for the primary key URL field in serializers."""

    requires_context = True

    def __call__(self, serializer_field: Field) -> int:
        """Get the current primary key from the request."""
        assert "pk" in serializer_field.context, (
            "CurrentPKURLDefault requires 'pk' in the serializer context."
        )
        return int(serializer_field.context["pk"])

    def __repr__(self) -> str:
        """Return a string representation of the default."""
        return "%s()" % self.__class__.__name__


class ProjectBaseSerializer(ModelSerializer):
    """
    Base serializer for Project instances.
    """

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Project
        fields = "__all__"


class ProjectListSerializer(ProjectBaseSerializer):
    """
    Serializer for listing Project instances.
    """

    users_count = SerializerMethodField(
        method_name="get_users_count",
    )
    author = CustomUserForeignSerializer()

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Project
        fields = (
            "id",
            "name",
            "author",
            "users_count",
        )

    def get_users_count(self, obj: Project) -> int:
        """
        Get the count of users associated with the project.

        Parameters:
            obj: Project
                The Project instance.

        Returns:
            int
                The count of users.
        """
        return getattr(obj, "users_count", 0)


class ProjectCreateSerializer(ProjectBaseSerializer):
    """
    Serializer for creating Project instances.
    """

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Project
        fields = (
            "id",
            "name",
            "author",
            "users",
        )


class ProjectUpdateSerializer(ProjectBaseSerializer):
    """
    Serializer for updating Project instances.
    """

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Project
        fields = (
            "name",
        )


class TaskBaseSerializer(ModelSerializer):
    """
    Base serializer for Task instances.
    """

    status = SerializerMethodField(read_only=True)

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Task
        fields = "__all__"

    def get_status(self, obj: Task) -> dict[str, int | str]:
        """
        Get the status of the task as a dictionary.

        Parameters:
            obj: Task
                The Task instance. 
        Returns:
            dict
                A dictionary containing the status id and label.
        """
        return obj.get_status_as_dict()


class TaskListSerializer(TaskBaseSerializer):
    """
    Serializer for listing Task instances.
    """

    assignees = CustomUserForeignSerializer(many=True)

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "status",
            "project",
            # "subtasks",
            "project",
            "assignees",
        )


class TaskCreateSerializer(TaskBaseSerializer):
    """
    Serializer for creating Task instances.
    """

    project = IntegerField(
        source="project_id",
        default=CurrentPKURLDefault(),
        required=False,
    )

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "status",
            "parent",
            "project",
            "assignees",
        )
        read_only_fields = (
            "id",
            "project",
        )
