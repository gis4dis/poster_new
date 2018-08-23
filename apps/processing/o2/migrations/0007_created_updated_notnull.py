# Generated by Django 2.0.3 on 2018-08-08 11:55

from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('o2', '0006_created_updated_notnull'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilityobservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=False),
        ),
        migrations.AlterField(
            model_name='sociodemoobservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=False),
        ),
        migrations.AlterField(
            model_name='mobilityobservation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=False),
        ),
        migrations.AlterField(
            model_name='sociodemoobservation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=False),
        )
    ]
