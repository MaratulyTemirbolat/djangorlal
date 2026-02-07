from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0005_add_company_to_companies'),
    ]

    operations = [
        migrations.RunSQL("SELECT 1;"),  # Dummy SQL to ensure the migration runs
        # Enable btree_gist extension for GIST index support on integer types
        # migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS btree_gist;"),
        # Prevent overlapping subscriptions for the same company
        # migrations.RunSQL(
        #     sql="ALTER TABLE companies_subscription ADD CONSTRAINT prevent_overlapping_subscriptions EXCLUDE USING GIST (company_id WITH =, daterange(start_date, end_date, '[)') WITH &&);",
        #     reverse_sql="ALTER TABLE companies_subscription DROP CONSTRAINT IF EXISTS prevent_overlapping_subscriptions;",
        # ),
    ]
