# Generated by Django 2.1.5 on 2019-03-25 14:08

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('rsd', '0012_delete_agg_add_unique'),
    ]

    operations = [
        migrations.RunSQL("""
        	TRUNCATE rsd_eventobservation_related_observations;
        """),
        migrations.RunSQL("""
        	TRUNCATE rsd_numberofeventsobservation_related_observations;
        """),
    ]
