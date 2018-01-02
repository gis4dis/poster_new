# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-21 14:22
from __future__ import unicode_literals

import apps.processing.ala.models
import django.contrib.postgres.fields.ranges
from django.db import migrations
from psycopg2.extras import DateTimeTZRange

def update_phenomenon_time_range():
    sql_statements = """
BEGIN;
update ala_observation
set phenomenon_time_range=tstzrange(phenomenon_time, phenomenon_time_to, '[]')
where phenomenon_time = phenomenon_time_to;
update ala_observation
set phenomenon_time_range=tstzrange(phenomenon_time, phenomenon_time_to, '[)')
where phenomenon_time != phenomenon_time_to;
END;
"""
    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('ala', '0006_result_null_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='phenomenon_time_range',
            field=django.contrib.postgres.fields.ranges.DateTimeRangeField(default=DateTimeTZRange(),
                                                                           help_text='Datetime range when the observation was captured.'),
        ),
        migrations.RunSQL(update_phenomenon_time_range()),
        migrations.AlterModelOptions(
            name='observation',
            options={'get_latest_by': 'phenomenon_time_range', 'ordering': ['-phenomenon_time_range', 'feature_of_interest', 'procedure', 'observed_property']},
        ),
        migrations.AlterUniqueTogether(
            name='observation',
            unique_together=set([('phenomenon_time_range', 'observed_property', 'feature_of_interest', 'procedure')]),
        ),
        migrations.RemoveField(
            model_name='observation',
            name='phenomenon_time',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='phenomenon_time_to',
        ),
    ]
