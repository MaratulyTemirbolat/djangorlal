# Python modules
from typing import Any

# Django modules
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    ForeignKey,
    SET_NULL,
    ManyToManyField,
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Project modules
from apps.abstracts.models import AbstractBaseModel
from apps.auths.validators import (
    validate_email_domain,
    validate_email_payload_not_in_full_name,
)


class CustomUserManager(BaseUserManager):
    """Custom User Manager to make database requests."""

    def __obtain_user_instance(
        self,
        email: str,
        full_name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'CustomUser':
        """Get user instance."""
        if not email:
            raise ValidationError(
                message="Email field is required", code="email_empty"
            )
        if not full_name:
            raise ValidationError(
                message="Full name name is required.", code="full_name_empty"
            )

        new_user: 'CustomUser' = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            password=password,
            **kwargs,
        )
        return new_user

    def create_user(
        self,
        email: str,
        full_name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'CustomUser':
        """Create Custom user. TODO where is this used?"""
        new_user: 'CustomUser' = self.__obtain_user_instance(
            email=email,
            full_name=full_name,
            password=password,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def create_superuser(
        self,
        email: str,
        full_name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'CustomUser':
        """Create super user. Used by manage.py createsuperuser."""
        new_user: 'CustomUser' = self.__obtain_user_instance(
            email=email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_superuser=True,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user


class Company(AbstractBaseModel):
    """Company model representing a company in the system."""

    name = CharField(
        max_length=150,
        unique=True,
        verbose_name="Company name",
        help_text="Name of the company",
    )

    class Meta:
        """Meta options for Company model."""

        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["-created_at"]


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom user model extending AbstractBaseModel.
    """
    EMAIL_MAX_LENGTH = 150
    FULL_NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 254

    PREFERRED_LANGUAGES = ["en", "ru", "kz"]

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[validate_email_domain],
        verbose_name=_("Email address"),
        help_text=_("User's email address"),
    )
    full_name = CharField(
        max_length=FULL_NAME_MAX_LENGTH,
        verbose_name=_("Full name"),
        help_text=_("User's full name"),
    )
    password = CharField(
        max_length=PASSWORD_MAX_LENGTH,
        validators=[validate_password],
        verbose_name=_("Password"),
        help_text=_("User's hash representation of the password"),
    )
    # True iff the user is part of the corporoom team, allowing them to access the admin panel
    is_staff = BooleanField(
        default=False,
        verbose_name=_("Staff status"),
        help_text=_("True if the user is an admin and has an access to the admin panel"),
    )
    # True iff the user can make requests to the backend (include in company)
    is_active = BooleanField(
        default=True,
        verbose_name=_("Active status"),
        help_text=_("True if the user is active and has an access to request data"),
    )
    company = ForeignKey(
        to=Company,
        on_delete=SET_NULL,
        null=True,
        verbose_name=_("Company"),
        help_text=_("Company the user belongs to"),
    )
    companies = ManyToManyField(
        to=Company,
        related_name="users",
        blank=True,
        verbose_name=_("Companies"),
        help_text=_("Companies the user belongs to"),
    )
    preferred_language = CharField(
        max_length=10,
        choices=[(lang, lang) for lang in PREFERRED_LANGUAGES],
        default="en",
        verbose_name=_("Preferred language"),
        help_text=_("User's preferred language"),
    )

    REQUIRED_FIELDS = ["full_name"]
    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    class Meta:
        """Meta options for CustomUser model."""

        verbose_name = _("Custom User")
        verbose_name_plural = _("Custom Users")
        ordering = ["-created_at"]

    def clean(self) -> None:
        """Validate the model instance before saving."""
        validate_email_payload_not_in_full_name(
            email=self.email,
            full_name=self.full_name,
        )
        return super().clean()
