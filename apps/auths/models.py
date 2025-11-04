# Python modules

# Django modules
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Project modules
from apps.abstracts.models import AbstractBaseModel
from apps.auths.validators import validate_email_domain


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom user model extending AbstractBaseModel.
    """
    EMAIL_MAX_LENGTH = 150
    FULL_NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 254

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[validate_email_domain],
        verbose_name="Email address",
        help_text="User's email address",
    )
    full_name = CharField(
        max_length=FULL_NAME_MAX_LENGTH,
        verbose_name="Full name",
    )
    password = CharField(
        max_length=PASSWORD_MAX_LENGTH,
        verbose_name="Password",
        help_text="User's hash representation of the password",
    )
    # True iff the user is part of the corporoom team, allowing them to access the admin panel
    is_staff = BooleanField(
        default=False,
        verbose_name="Staff status",
        help_text="True if the user is an admin and has an access to the admin panel",
    )
    # True iff the user can make requests to the backend (include in company)
    is_active = BooleanField(
        default=True,
        verbose_name="Active status",
        help_text="True if the user is active and has an access to request data",
    )

    REQUIRED_FIELDS = ["full_name"]
    USERNAME_FIELD = "email"

    class Meta:
        """Meta options for CustomUser model."""

        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
        ordering = ["-created_at"]
