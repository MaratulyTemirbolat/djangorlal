# Python modules
from typing import Any, Optional

# Django modules
from django.utils.translation import gettext_lazy, gettext

# Django REST Framework
from rest_framework.serializers import Serializer, CharField, EmailField, IntegerField, ListField
from rest_framework.exceptions import ValidationError

# Project modules
from apps.auths.models import CustomUser


class UserLoginResponseSerializer(Serializer):
    """
    Serializer for user login response.
    """

    id = IntegerField()
    full_name = CharField()
    email = EmailField()
    access = CharField()
    refresh = CharField()

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "id",
            "full_name",
            "email",
            "access",
            "refresh",
        )


class UserLoginErrorsSerializer(Serializer):
    """
    Serializer for user login errors.
    """

    email = ListField(
        child=CharField(),
        required=False,
    )
    password = ListField(
        child=CharField(),
        required=False,
    )

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "email",
            "password",
        )


class HTTP405MethodNotAllowedSerializer(Serializer):
    """
    Serializer for HTTP 405 Method Not Allowed response.
    """

    detail = CharField()

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "detail",
        )

class UserLoginSerializer(Serializer):
    """
    Serializer for user login.
    """

    email = EmailField(
        required=True,
        max_length=CustomUser.EMAIL_MAX_LENGTH,
    )
    password = CharField(
        required=True,
        max_length=CustomUser.PASSWORD_MAX_LENGTH,
    )

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "email",
            "password",
        )

    def validate_email(self, value: str) -> str:
        """Validates the email field."""
        return value.lower()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validates the input data."""
        email: str = attrs["email"]
        password: str = attrs["password"]

        user: Optional[CustomUser] = CustomUser.objects.filter(email=email).first()

        if not user:
            raise ValidationError(
                detail={
                    "email": [gettext("User with email %(email)s does not exist.") % {"email": email}]
                }
            )
        gettext("Dear %s, your order %s is ready.") % ("John", "#1234")
        gettext("Dear %(name)s, your order %(order)s is ready.") % {"name": "John", "order": "#1234"}
        # Дорогой Джон, ваш заказ #1234 готов.
        # "%s тапсырысыныз дайын, %s" % ("#1234", "Джон")
        # "%(order)s тапсырысыныз дайын, %(name)s"

        if not user.check_password(raw_password=password):
            raise ValidationError(
                detail={
                    "password": [gettext("Incorrect password.")]
                }
            )

        attrs["user"] = user    

        return super().validate(attrs)
