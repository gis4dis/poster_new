# Generated by Django 2.0.3 on 2018-09-18 15:57

import apps.common.models
import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import relativedeltafield


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_topic'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zero', models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0, tzinfo=utc))),
                ('frequency', relativedeltafield.RelativeDeltaField(default=apps.common.models.default_relative_delta_hour)),
                ('range_from', relativedeltafield.RelativeDeltaField(default=apps.common.models.default_relative_delta_zero)),
                ('range_to', relativedeltafield.RelativeDeltaField(default=apps.common.models.default_relative_delta_hour)),
            ],
        ),
    ]