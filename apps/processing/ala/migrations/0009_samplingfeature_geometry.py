# Generated by Django 2.0.3 on 2018-05-09 19:28

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ala', '0008_auto_20180214_0043'),
    ]

    operations = [
        migrations.AddField(
            model_name='samplingfeature',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Spatial information about feature.', null=True, srid=3857),
        ),
    ]
