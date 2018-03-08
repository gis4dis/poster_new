# Generated by Django 2.0.2 on 2018-03-03 17:33

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsd', '0002_auto_20180301_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminunit',
            name='geometry',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text='Spatial information about feature.', srid=3857),
        ),
        migrations.AlterField(
            model_name='eventextent',
            name='admin_units',
            field=models.ManyToManyField(related_name='rsd_admin_units', to='rsd.AdminUnit'),
        ),
        migrations.AlterField(
            model_name='eventobservation',
            name='category',
            field=models.ForeignKey(editable=False, help_text='Type of an event.', on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_category', to='rsd.EventCategory'),
        ),
        migrations.AlterField(
            model_name='eventobservation',
            name='feature_of_interest',
            field=models.ForeignKey(editable=False, help_text='Admin units of Brno+Brno-venkov+D1', on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_feature_of_interest', to='rsd.EventExtent'),
        ),
        migrations.AlterField(
            model_name='eventobservation',
            name='result',
            field=models.ForeignKey(editable=False, help_text='Admin units of the event', on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_result', to='rsd.EventExtent'),
        ),
    ]