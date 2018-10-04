from __future__ import absolute_import, unicode_literals
from celery.task import task, group
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage
from django.core.management import call_command
from datetime import date, timedelta, datetime
from apps.processing.pmo.models import WatercourseObservation
from apps.processing.pmo.util import util
from apps.utils.time import UTC_P0100
logger = get_task_logger(__name__)

@task(name="pmo.import")
def import_default(*args):
    try:
        call_command('pmo_import', *args)
    except Exception as e:
        logger.error(e)


def get_last_record():
    try:
        last_item = WatercourseObservation.objects.all().latest('phenomenon_time_range')
    except WatercourseObservation.DoesNotExist:
        last_item = None
    return last_item


basedir_def = '/apps.processing.pmo/'


@task(name="pmo.import_observation")
def import_observation(date_str):
    date = datetime.strptime(date_str, "%Y%m%d").date()
    logger.info('Importing file: ' + str(date))
    util.load(date)


@task(name="pmo.import_observations")
def import_observations():
    last_record = get_last_record()
    dates_to_import = []

    if last_record is not None:
        start_day = last_record.phenomenon_time_range.lower
        start_day = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
        start_day = start_day + timedelta(1)

        now = datetime.now()
        now = now.replace(tzinfo=UTC_P0100)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_start = (today - timedelta(days=now.weekday()))
        day_to = this_week_start

        day = start_day

        while day < day_to:
            day_str = day.strftime("%Y%m%d")
            path = basedir_def + day_str + '/HOD.dat'
            if default_storage.exists(path):
                dates_to_import.append(day_str)
            day += timedelta(1)
    else:
        listed = default_storage.listdir(basedir_def)
        for filename in listed:
            if filename.is_dir:
                folder_path = filename.object_name
                path = folder_path + '/HOD.dat'
                if default_storage.exists(path):
                    day_str = filename.object_name.strip("/").split('/')[-1]
                    dates_to_import.append(day_str)

    try:
        g = group(import_observation.s(date) for date in dates_to_import)
        g.apply_async()
    except Exception as e:
        logger.error(e)


