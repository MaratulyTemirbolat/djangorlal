# Python modules + Third party modules

# Django modules
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    TextField,
    IntegerField,
    ForeignKey,
    ManyToManyField,
    UniqueConstraint,
    PROTECT,
    CASCADE,
)
from django.contrib.auth.models import User

# Project modules


class Project(Model):
    """
    Project database (table) model.
    """

    NAME_MAX_LEN = 100

    name = CharField(
        max_length=NAME_MAX_LEN,
    )
    author = ForeignKey(
        to=User,
        on_delete=PROTECT,
        related_name="owned_projects",
    )
    users = ManyToManyField(
        to=User,
        blank=True,
        related_name="joined_projects",
    )
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


class Task(Model):
    """
    Task database (table) model.
    """

    NAME_MAX_LEN = 200
    STATUS_TODO = 1
    STATUS_TODO_LABEL = "To Do"
    STATUS_IN_PROGRESS = 2
    STATUS_IN_PROGRESS_LABEL = "In Progress"
    STATUS_DONE = 3
    STATUS_DONE_LABEL = "Done"
    # STATUS_CHOICES = (
    #     (STATUS_TODO, STATUS_TODO_LABEL),
    #     (STATUS_IN_PROGRESS, STATUS_IN_PROGRESS_LABEL),
    #     (STATUS_DONE, STATUS_DONE_LABEL),
    # )
    STATUS_CHOICES = {
        STATUS_TODO: STATUS_TODO_LABEL,
        STATUS_IN_PROGRESS: STATUS_IN_PROGRESS_LABEL,
        STATUS_DONE: STATUS_DONE_LABEL,
    }

    name = CharField(
        max_length=NAME_MAX_LEN,
        db_index=True,
    )
    description = TextField(
        blank=True,
        default="",
    )
    status = IntegerField(
        default=STATUS_TODO,
        choices=STATUS_CHOICES,
    )
    parent = ForeignKey(
        to="self",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    project = ForeignKey(
        to=Project,
        on_delete=CASCADE,
    )
    assignees = ManyToManyField(
        to=User,
        through="UserTask",
        through_fields=("task", "user"),
        blank=True,
    )
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


class UserTask(Model):
    """
    UserTask database (table) model.
    """

    task = ForeignKey(
        to=Task,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        to=User,
        on_delete=CASCADE,
    )
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
        """Customization of the model's meta data."""

        # unique_together = ("task", "user")
        constraints = [
            UniqueConstraint(
                fields=["task", "user"],
                name="unique_task_user",
            ),
        ]
