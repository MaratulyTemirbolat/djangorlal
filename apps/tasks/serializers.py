# Django REST Framework modules
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField
)

# Project modules
from apps.tasks.models import Project
from apps.abstracts.serializers import CustomUserForeignSerializer


class ProjectListSerializer(ModelSerializer):
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


class ProjectCreateSerializer(ModelSerializer):
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


class ProjectUpdateSerializer(ModelSerializer):
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
