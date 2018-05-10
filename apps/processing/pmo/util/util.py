# coding=utf-8
import logging
from datetime import timedelta, datetime
from django.db.utils import IntegrityError
from apps.common.models import Process, Property
from apps.utils.obj import *
from psycopg2.extras import DateTimeTZRange
from django.core.files.storage import default_storage
import csv
from apps.processing.pmo.models import WatercourseObservation, WatercourseStation
import io

logger = logging.getLogger(__name__)

props_def = [
    ('water_level', {"name": 'water level', 'unit': 'm'}),
    ('stream_flow', {"name": 'stream flow', 'unit': 'm3/s'})
]

props_data_types = {
    '17': 'water_level',
    '29': 'stream_flow'
}

processes_def = [
    ('measure', {'name': u'measuring'})
]

basedir_def = '/pmo/'


def get_or_create_props():
    return get_or_create_objs(Property, props_def, 'name_id')


def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')


def load(day):

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
            except:
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
                        logger.error('Propety with name %s does not exist.', observed_property)
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

                            obs, created = WatercourseObservation.objects.update_or_create(
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
                                )
                            )
                            #logger.warning('Error in creating observation from measure %s', measure_id)
                            pass
                else:
                    logger.error('Unknown measure code %s', code)
    else:
        logger.error("Error file path: %s not found", path)
