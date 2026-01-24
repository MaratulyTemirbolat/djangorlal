# Python modules
from typing import Type, Any

# Django modules
from django.db.models.signals import post_save

# Project modules
from apps.tasks.models import Task


def notify_user_task_creation(
    sender: Type[Task],
    instance: Task,
    created: bool,
    **kwargs: dict[str, Any]
) -> None:
    """
    Signal handler to notify when a UserTask is created.

    Parameters:
        sender: Model class
            The model class that sent the signal.
        instance: Model instance
            The actual instance being saved.
        created: bool
            A boolean indicating whether a new record was created.
        **kwargs: dict
            Additional keyword arguments.
    """
    if created:
        # Here you can implement the logic to notify users.
        # For example, sending an email or creating a notification entry.
        print(f"UserTask created with ID: {instance.id}")

post_save.connect(notify_user_task_creation, sender=Task)
