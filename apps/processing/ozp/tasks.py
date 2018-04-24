from __future__ import absolute_import, unicode_literals

from datetime import date, timedelta

from celery.task import task, group
from celery.utils.log import get_task_logger

from apps.processing.ala.models import SamplingFeature
from apps.processing.ala.util import util

logger = get_task_logger(__name__)


@task(name="ala.import_all_stations")
def import_all_stations(day=None):
    stations = util.get_or_create_stations()

    try:
        # Call another Celery tasks as GROUP. For more info see Celery documentation.
        g = group(import_station.s(station.pk, day) for station in stations)
        g.apply_async()
    except Exception as e:
        logger.error(e)


@task(name="ala.import_single_station")
def import_station(station_id, day):

    if day is None:
        day = date.today() - timedelta(1)

    try:
        station = SamplingFeature.objects.get(pk=station_id)
        logger.info('Importing data of {} ALA stations from {}.'.format(station, day))

        util.load(station, day)
        util.create_avgs(station, day)
    except SamplingFeature.DoesNotExist as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
