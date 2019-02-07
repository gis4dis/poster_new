
from django.core.management import call_command # Add this import
from django.db import migrations


def create_cache(apps, schema_editor):
    call_command('createcachetable', 'cache_table')
    pass


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_cache),
    ]

