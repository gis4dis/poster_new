# Generated by Django 2.1.5 on 2019-03-25 14:08

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ozp', '0006_delete_agg_create_unique_index'),
    ]

    operations = [
        migrations.RunSQL("""
        	TRUNCATE ozp_observation_related_observations;
        """),
    ]