# Generated by Django 2.0.3 on 2018-08-08 11:55

from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('rsd', '0005_number_of_events_observation'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventobservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='eventobservation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='numberofeventsobservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='numberofeventsobservation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunSQL("UPDATE rsd_eventobservation "
                          "SET created_at=CURRENT_TIMESTAMP"
                          ", updated_at=CURRENT_TIMESTAMP"),
        migrations.RunSQL("UPDATE rsd_numberofeventsobservation "
                          "SET created_at=CURRENT_TIMESTAMP"
                          ", updated_at=CURRENT_TIMESTAMP"),
    ]