from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = "Tasks management"

    def ready(self):
        from apps.tasks import signals  # noqa: F401
        return super().ready()