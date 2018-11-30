# coding=utf-8
import csv
import io
import logging
import os
from datetime import timedelta, datetime

from dateutil import relativedelta
from dateutil.parser import parse
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.utils import IntegrityError
from psycopg2.extras import DateTimeTZRange

from apps.common.models import Process, Property
from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.pmo.models import WatercourseObservation, WatercourseStation
from apps.processing.pmo.models import WeatherStation, WeatherObservation
from apps.utils.time import UTC_P0100

logger = logging.getLogger(__name__)

# https://github.com/gis4dis/poster/issues/111
# Substitute '/import/' for django.conf.settings.IMPORT_ROOT
basedir_def = os.path.join(settings.IMPORT_ROOT, 'apps.processing.pmo/', '')

props_data_types = {
    '17': 'water_level',
    '29': 'stream_flow'
}


def load_srazsae(day, basedir=basedir_def):
    day = day.strftime("%Y%m%d")

    get_or_create_processes()
    get_or_create_props()
    measure = Process.objects.get(name_id="measure")
    air_temperature = Property.objects.get(name_id="air_temperature")
    precipitation = Property.objects.get(name_id="precipitation")

    path = basedir + day + '/srazsae.dat'

    if default_storage.exists(path):
        csv_file = default_storage.open(name=path, mode='r')
        foo = csv_file.data.decode('utf-8')
        reader = csv.reader(io.StringIO(foo), delimiter=" ")
        rows = list(reader)

        for rid_x, row in enumerate(rows, 1):
            try:
                result = row[5]
                station_id = row[0]
                weather_station = WeatherStation.objects.get(id_by_provider=station_id)
                parsed = parse(row[2] + " " + row[3])
                time = parsed.astimezone(UTC_P0100)

                if row[1] == '32':
                    dt_range = DateTimeTZRange(time, time, bounds="[]")
                    observed_property = air_temperature
                else:
                    observed_property = precipitation
                    dt_range = DateTimeTZRange(time, time + timedelta(hours=1),
                                               bounds="[)")

                try:
                    defaults = {
                        'phenomenon_time_range': dt_range,
                        'observed_property': observed_property,
                        'feature_of_interest': weather_station,
                        'procedure': measure,
                        'result': result
                    }

                    WeatherObservation.objects.update_or_create(
                        phenomenon_time_range=dt_range,
                        observed_property=observed_property,
                        feature_of_interest=weather_station,
                        procedure=measure,
                        defaults=defaults
                    )

                except IntegrityError as e:
                    logger.warning(
                        "Error in creating srazsae observation from station_id {},"
                        "measure_date {}, measure_id {}".format(
                            station_id,
                            time,
                            row[4]
                        ), exc_info=True)
                    pass

            except WeatherStation.DoesNotExist:
                print('Error STATION WITH ID NOT FOUND: ', row[0])
    else:
        logger.error("Error file path: %s not found", path)


def load_hod(day):

    day = day.strftime("%Y%m%d")

    get_or_create_processes()
    get_or_create_props()

    process = Process.objects.get(name_id='measure')

    path = basedir_def + day + '/HOD.dat'

    if default_storage.exists(path):
        csv_file = default_storage.open(name=path, mode='r')
        foo = csv_file.data.decode('utf-8')

        reader = csv.reader(io.StringIO(foo), delimiter=' ')

        rows = list(reader)

        for rid_x, row in enumerate(rows, 1):
            station_id = row[0]
            code = row[1]
            measure_date = row[2]
            measure_time = row[3]
            measure_id = row[4]
            result = None
            result_null_reason = ''

            try:
                result = float(row[5])
            except Exception as e:
                logger.warning(e, exc_info=True)
                result_null_reason = 'invalid value in CSV'
                pass

            try:
                station = WatercourseStation.objects.get(id_by_provider=station_id)
            except WatercourseStation.DoesNotExist:
                logger.warning(
                    "WatercourseStation does not exist. Measure with values station_id {},"
                    "code {}, measure_date {}, measure_time {}, measure_id {} not imported".format(
                        station_id,
                        code,
                        measure_date,
                        measure_time,
                        measure_id
                    )
                )
                station = None
                pass

            if station:
                data_type = props_data_types.get(code)
                if data_type:
                    try:
                        observed_property = Property.objects.get(name_id=data_type)
                    except Property.DoesNotExist:
                        logger.error('Property with name %s does not exist.', data_type)
                        observed_property = None
                        pass

                    if observed_property:
                        time_str = measure_date + ' ' + measure_time
                        time_from = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
                        pt_range = DateTimeTZRange(time_from, time_from, '[]')

                        try:

                            defaults = {
                                'phenomenon_time_range': pt_range,
                                'observed_property': observed_property,
                                'feature_of_interest': station,
                                'procedure': process,
                                'result': result,
                                'result_null_reason': result_null_reason
                            }

                            WatercourseObservation.objects.update_or_create(
                                phenomenon_time_range=pt_range,
                                observed_property=observed_property,
                                feature_of_interest=station,
                                procedure=process,
                                defaults=defaults
                            )

                        except IntegrityError as e:
                            print(row)
                            logger.warning(
                                "Error in creating observation from station_id {},"
                                "code {}, measure_date {}, measure_time {}, measure_id {}".format(
                                    station_id,
                                    code,
                                    measure_date,
                                    measure_time,
                                    measure_id
                                ),
                                exc_info=True)
                            # logger.warning('Error in creating observation from measure %s', measure_id)
                            pass
                else:
                    logger.error('Unknown measure code %s', code)
    else:
        logger.error("Error file path: %s not found", path)


def parse_date_range(date_str):
    if len(date_str) == 4:
        day_from = parse(date_str).replace(day=1, month=1)
        day_to = day_from + relativedelta.relativedelta(years=1)
    elif len(date_str) == 7:
        day_from = parse(date_str).replace(day=1)
        day_to = day_from + relativedelta.relativedelta(months=1)
    else:
        day_from = parse(date_str)
        day_to = day_from + timedelta(1)
    return [day_from, day_to]
