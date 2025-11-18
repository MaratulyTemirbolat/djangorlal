# Django REST Framework modules
from rest_framework.serializers import ModelSerializer

# Project modules
from apps.auths.models import CustomUser


class CustomUserForeignSerializer(ModelSerializer):
    """
    Serializer for CustomUser foreign key representation.
    """

    class Meta:
        """
        Customize the serializer's metadata.
        """
        model = CustomUser
        fields = (
            "id",
            "email",
            "full_name",
            "created_at",
            "updated_at",
        )
