from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta, datetime

from celery.task import task, group
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management import call_command

from apps.processing.pmo.models import WatercourseObservation, WeatherObservation
from apps.processing.pmo.util import util
from apps.utils.time import UTC_P0100

logger = get_task_logger(__name__)


@task(name="pmo.import")
def import_default(*args):
    try:
        call_command('pmo_import', *args)
    except Exception as e:
        logger.critical(e)


def get_last_record(model):
    try:
        last_item = model.objects.all().latest('phenomenon_time_range')
    except model.DoesNotExist:
        last_item = None
    return last_item


# https://github.com/gis4dis/poster/issues/111
# Substitute '/import/' for django.conf.settings.IMPORT_ROOT
basedir_def = os.path.join(settings.IMPORT_ROOT, 'apps.processing.pmo/', '')


@task(name="pmo.import_hod_observation")
def import_hod_observation(date_str):
    date_obj = datetime.strptime(date_str, "%Y%m%d").date()
    logger.info('Importing HOD file: ' + str(date_obj))
    util.load_hod(date_obj)


@task(name="pmo.import_srazsae_observation")
def import_srazsae_observation(date_str):
    date = datetime.strptime(date_str, "%Y%m%d").date()
    logger.info('Importing srazsae file: ' + str(date))
    util.load_srazsae(date)


def get_dates_to_import(model, file):
    last_record = get_last_record(model)
    dates_to_import = []

    if last_record is not None:
        start_day = last_record.phenomenon_time_range.lower
        start_day = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
        start_day = start_day + timedelta(1)

        now = datetime.now()
        now = now.replace(tzinfo=UTC_P0100)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_to = today

        day = start_day

        while day < day_to:
            day_str = day.strftime("%Y%m%d")
            path = basedir_def + day_str + '/' + str(file)
            if default_storage.exists(path):
                dates_to_import.append(day_str)
            day += timedelta(1)
    else:
        listed = default_storage.listdir(basedir_def)
        for filename in listed:
            if filename.is_dir:
                folder_path = filename.object_name
                path = folder_path + '/' + str(file)
                if default_storage.exists(path):
                    day_str = filename.object_name.strip("/").split('/')[-1]
                    dates_to_import.append(day_str)

    return dates_to_import


@task(name="pmo.import_observations")
def import_observations():
    watercourse_dates_to_import = get_dates_to_import(WatercourseObservation, 'HOD.dat')
    srazsae_dates_to_import = get_dates_to_import(WeatherObservation, 'srazsae.dat')

    try:
        g = group(import_hod_observation.s(date) for date in watercourse_dates_to_import)
        g.apply_async()
    except Exception as e:
        logger.critical(e)

    try:
        g = group(import_srazsae_observation.s(date) for date in srazsae_dates_to_import)
        g.apply_async()
    except Exception as e:
        logger.critical(e)
