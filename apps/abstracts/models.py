# Python modules
from typing import Any

# from datetime import datetime, timezone

# Django modules
from django.db.models import Model, DateTimeField
from django.utils import timezone as django_timezone


class AbstractBaseModel(Model):
    """
    Abstract base model with common fields.
    """

    created_at = DateTimeField(
        auto_now_add=True
    )
    updated_at = DateTimeField(
        auto_now=True
    )
    deleted_at = DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        """Meta class for AbstractBaseModel."""

        abstract = True

    def delete(self, *args: tuple[Any, ...], **kwargs: dict[Any, Any]) -> None:
        """Soft delete the object by setting deleted_at timestamp."""

        # self.deleted_at = datetime.now(timezone.utc)  # Purely python way
        self.deleted_at = django_timezone.now()
        self.save(update_fields=["deleted_at"])

