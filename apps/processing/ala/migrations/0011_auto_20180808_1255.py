# Generated by Django 2.0.3 on 2018-08-08 11:55

from django.db import migrations, models
from django.utils import timezone


def populate_dates(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Observation = apps.get_model('ala', 'Observation')
    for o in Observation.objects.all():
        o.created_at = timezone.now()
        o.updated_at = timezone.now()
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ala', '0010_update_aggregation_procedures'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(populate_dates),
        migrations.AlterField(
            model_name='observation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, blank=True),
        ),
        migrations.AlterField(
            model_name='observation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, blank=True),
        )
    ]
