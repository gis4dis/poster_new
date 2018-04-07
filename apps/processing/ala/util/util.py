# coding=utf-8
import codecs
import csv
import logging
import requests
from contextlib import closing
from datetime import timedelta, datetime
from dateutil.parser import parse
from decimal import Decimal
from django.db.utils import IntegrityError

from apps.processing.ala.models import SamplingFeature, Observation
from apps.common.models import Process, Property
from apps.utils.obj import *
from apps.utils.time import UTC_P0100
from psycopg2.extras import DateTimeTZRange
from apps.common.aggregate import aggregate

logger = logging.getLogger(__name__)

stations_def = [
    ('11359201', {'name': u'Brno, botanical garden PřF MU'}),
    ('11359196', {'name': u'Brno, Kraví Hora'}),
    ('11359205', {'name': u'Brno, FF MU, Arne Nováka'}),
    ('11359192', {'name': u'Brno, Schodová'}),
    ('11359202', {'name': u'Brno, Hroznová'}),
    ('11359132', {'name': u'Brno, Mendlovo nám.'}),
]

props_def = [
    ('precipitation', {"name": 'precipitation', 'unit': 'mm'}),
    ('air_temperature', {"name": 'air temperature', 'unit': '°C'}),
    ('air_humidity', {"name": 'air humidity', 'unit': '?'}),
    ('ground_air_temperature',
     {"name": 'ground air temperature', 'unit': '°C'}),
    ('soil_temperature', {"name": 'soil temperature', 'unit': '°C'}),
    ('power_voltage', {"name": 'power voltage', 'unit': 'V'}),
    ('wind_speed', {"name": 'wind speed', "unit": 'm/s'}),
    ('wind_direction', {"name": 'wind direction', "unit": '°', "default_average": "apps.common.aggregate.circle_mean"}),
    ('solar_energy', {"name": 'solar energy', "unit": 'W/m2'}),
]

props_to_provider_idx = {
    '11359201': {
        'precipitation': 1,
        'air_temperature': 2,
        'air_humidity': 3,
        'ground_air_temperature': 6,
        'soil_temperature': 7,
        'power_voltage': 8,
    },
    '11359196': {
        'precipitation': 1,
        'air_temperature': 2,
        'air_humidity': 3,
        'ground_air_temperature': 6,
        'soil_temperature': 7,
        'power_voltage': 8,
    },
    '11359205': {
        'precipitation': 1,
        'air_temperature': 2,
        'air_humidity': 3,
        'ground_air_temperature': 6,
        'soil_temperature': 7,
        'power_voltage': 8,
    },
    '11359192': {
        'precipitation': 1,
        'air_temperature': 2,
        'air_humidity': 3,
        'ground_air_temperature': 6,
        'soil_temperature': 7,
        'power_voltage': 8,
    },
    '11359202': {
        'precipitation': 6,
        'air_temperature': 1,
        'air_humidity': 7,
        'ground_air_temperature': 2,
        'soil_temperature': 4,
        'power_voltage': 12,
        'wind_speed': 8,
        'wind_direction': 11,
        'solar_energy': 9,
    },
    '11359132': {
        'precipitation': 1,
        'air_temperature': 2,
        'air_humidity': 3,
        'power_voltage': 5,
    },
}

station_interval = {
    '11359201': 10 * 60,
    '11359196': 10 * 60,
    '11359205': 10 * 60,
    '11359192': 10 * 60,
    '11359202': 15 * 60,
    '11359132': 10 * 60,
}
# 6 prop * 7 per hour * 4 st = 168
# 6 prop * 5 per hour * 1 st =  30
# 4 prop * 7 per hour * 1 st =  28
# TOTAL 226 per hour * 24 = 5424 per day

processes_def = [
    ('measure', {'name': u'measuring'}),
    ('avg_hour', {'name': u'hourly average'}),
    ('avg_day', {'name': u'daily average'}),
]


def get_or_create_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'id_by_provider')


def get_or_create_props():
    return get_or_create_objs(Property, props_def, 'name_id')


def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')


def load(station, day):
    """Load and save ALA observations for given station and date."""
    get_or_create_processes()
    process = Process.objects.get(name_id='measure')

    from_naive = datetime.combine(day, datetime.min.time())
    to_naive = datetime.combine(day + timedelta(1), datetime.min.time())

    from_aware = from_naive.replace(tzinfo=UTC_P0100)
    to_aware = to_naive.replace(tzinfo=UTC_P0100)

    from_s = int(from_aware.timestamp())
    to_s = int(to_aware.timestamp())

    url = 'http://a.la-a.la/chart/data_csvcz.php?probe={}&t1={}&t2={}'.format(
        station.id_by_provider, from_s, to_s)

    logger.info('Downloading {}'.format(url))
    props = get_or_create_props()

    with closing(requests.get(url, stream=True)) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'),
                            delimiter=';')
        rows = list(reader)
        num_rows = len(rows)
        expected_rows = 24 * 60 * 60 // \
                        station_interval[station.id_by_provider] + 1
        if num_rows != expected_rows:
            logger.warning("Expected {} rows, found {}. Station {}.".format(
                expected_rows, num_rows, station.id_by_provider))
        prev_time = None

        for ridx, row in enumerate(rows, 1):
            time = parse(row[0], dayfirst=True).replace(tzinfo=UTC_P0100)
            for prop in props:
                if prev_time is None and prop.name_id == 'precipitation':
                    continue
                if ridx == num_rows and prop.name_id != 'precipitation':
                    continue
                time_from = \
                    prev_time if prop.name_id == 'precipitation' else time
                time_to = time
                time_range_boundary = '[]' if time_from == time_to else '[)'
                pt_range = DateTimeTZRange(time_from, time_to, time_range_boundary)
                if (prop.name_id not in
                        props_to_provider_idx[station.id_by_provider]):
                    continue
                prop_idx = \
                    props_to_provider_idx[station.id_by_provider][prop.name_id]
                res_str = row[prop_idx].replace(',', '.')
                if res_str == '':
                    result = None
                    result_null_reason = 'empty string in CSV'
                else:
                    try:
                        result = Decimal(res_str)
                        result_null_reason = ''
                    except Exception as e:
                        result = None
                        result_null_reason = 'invalid string in CSV'
                if result is None:
                    logger.warning(
                        "Result_null_reason of measuring, station {}, "
                        "property {}, phenomenon time {}: {}".format(
                            station.id_by_provider,
                            prop.name_id,
                            time_from,
                            result_null_reason
                        )
                    )
                try:
                    defaults = {
                        'phenomenon_time_range': pt_range,
                        'observed_property': prop,
                        'feature_of_interest': station,
                        'procedure': process,
                        'result': result,
                        'result_null_reason': result_null_reason
                    }

                    obs, created = Observation.objects.update_or_create(
                        phenomenon_time_range=pt_range,
                        observed_property=prop,
                        feature_of_interest=station,
                        procedure=process,
                        defaults=defaults
                    )

                except IntegrityError as e:
                    pass
            prev_time = time


def create_avgs(station, day):
    """Create hourly averages for given station and date."""
    if station is None:
        stations = get_or_create_stations()
        station = stations[0]

    from_naive = datetime.combine(day, datetime.min.time())

    props = get_or_create_props()
    measure_process = Process.objects.get(name_id='measure')

    for prop in props:
        from_aware = from_naive.replace(tzinfo=UTC_P0100)

        if prop.name_id not in props_to_provider_idx[station.id_by_provider]:
            continue

        process = Process.objects.get(name_id='avg_hour')

        for i in range(0, 24):
            to_aware = from_aware + timedelta(hours=1)
            pt_range = DateTimeTZRange(from_aware, to_aware)

            obss = Observation.objects.filter(
                phenomenon_time_range__contained_by=pt_range,
                feature_of_interest=station,
                observed_property=prop,
                procedure=measure_process
            )
            expected_values = 60 * 60 // \
                              station_interval[station.id_by_provider]
            if len(obss) != expected_values:
                result = None
                result_null_reason = 'missing observations'
            else:
                values = list(map(lambda o: o.result, obss))
                values = list(filter(lambda v: v is not None, values))
                if (len(values) == 0):
                    result = None
                    result_null_reason = 'only null values'
                else:
                    result, result_null_reason = aggregate(prop, values)

            if result is None:
                logger.warning(
                    "Result_null_reason of hourly average, "
                    "station {}, property {}, hour {}: {}".format(
                        station.id_by_provider,
                        prop.name_id,
                        i,
                        result_null_reason
                    )
                )

            try:
                defaults = {
                    'phenomenon_time_range': pt_range,
                    'observed_property': prop,
                    'feature_of_interest': station,
                    'procedure': process,
                    'result': result,
                    'result_null_reason': result_null_reason
                }

                obs, created = Observation.objects.update_or_create(
                    phenomenon_time_range=pt_range,
                    observed_property=prop,
                    feature_of_interest=station,
                    procedure=process,
                    defaults=defaults
                )

                obs.related_observations.set(obss)
            except IntegrityError as e:
                pass

            from_aware = to_aware
