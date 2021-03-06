# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 21:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.datetime_safe
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('code', models.SlugField(max_length=32, unique=True)),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProviderLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=False, editable=False)),
                ('content_type', models.CharField(default=b'application/txt', max_length=32)),
                ('body', models.TextField(blank=True)),
                ('file_name', models.CharField(max_length=32)),
                ('file_path', models.CharField(max_length=256)),
                ('ext', models.CharField(max_length=16)),
                ('received_time', models.DateTimeField(default=django.utils.datetime_safe.datetime.now)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='importing.Provider')),
            ],
        ),
    ]
