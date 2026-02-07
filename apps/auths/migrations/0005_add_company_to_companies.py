from typing import Type, TYPE_CHECKING
from django.db import migrations, models
from django.db.migrations.state import StateApps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

if TYPE_CHECKING:
    from apps.auths.models import CustomUser, Company


def add_company_to_companies(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Add company to companies."""
    CustomUser: Type["CustomUser"]  = apps.get_model("auths", "CustomUser")
    Company: Type["Company"] = apps.get_model("auths", "Company")

    for user in CustomUser.objects.all():
        if user.company:
            user.companies.add(user.company)


def remove_company_from_companies(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Remove company from companies."""
    CustomUser: Type["CustomUser"]  = apps.get_model("auths", "CustomUser")

    for user in CustomUser.objects.all():
        user.companies.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0004_customuser_companies'),
    ]

    operations = [
        migrations.RunPython(
            code=add_company_to_companies,
            # reverse_code=migrations.RunPython.noop,
            reverse_code=remove_company_from_companies,
        )
    ]
