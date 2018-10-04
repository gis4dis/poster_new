from __future__ import absolute_import, unicode_literals
from celery.task import task, group
from django.core.files.storage import default_storage
from django.core.management import call_command
from celery.utils.log import get_task_logger
from apps.processing.pmo.models import WatercourseObservation
from datetime import date, timedelta, datetime
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


@task(name="pmo.import_observations")
def import_observations(*args):
    last_record = get_last_record()

    if not last_record is None:
        print('LAST ITEM:', last_record)
        print('phenomenon_time_from: ', last_record.phenomenon_time_range.lower)

        start_day = last_record.phenomenon_time_range.lower
        start_day = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = (start_day - timedelta(days=start_day.weekday()))
        last_week_start = week_start + timedelta(weeks=-1)

        now = datetime.now()
        now = now.replace(tzinfo=UTC_P0100)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_start = (today - timedelta(days=now.weekday()))

        day_from = last_week_start
        day_to = this_week_start

        day = day_from
        logger.info('Importing observations of PMO watercourse observation')

        while day < day_to:
            day_str = day.strftime("%Y%m%d")
            path = basedir_def + day_str + '/HOD.dat'
            if default_storage.exists(path):
                print('Importing file: ', path)
                # util.load(day)
            # else:
            #    print('EXISTS: ', False)

            # TODO - add 1 or 7?
            day += timedelta(7)
    else:
        # TODO V1
        '''
        import boto3
        bucket_name = 'MINIO_STORAGE_MEDIA_BUCKET_NAME'
        s3 = boto3.client("s3")
        all_objects = s3.list_objects(Bucket=bucket_name)
        print('ALLLL: ', all_objects)
        '''

        # TODO V2
        # define default startdate and until today iterate

        #
        # if default_storage.exists(path):
        print('LIST DIR....')
