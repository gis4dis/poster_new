# coding=utf-8
import codecs
import csv
import logging
from contextlib import closing
from datetime import timedelta, datetime
from decimal import Decimal

import requests
from dateutil.parser import parse
from django.contrib.gis.geos import GEOSGeometry
from django.db.utils import IntegrityError
from psycopg2.extras import DateTimeTZRange

from apps.common.aggregate import aggregate
from apps.common.models import Process
from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.ala.models import SamplingFeature, Observation
from apps.utils.obj import *
from apps.utils.time import UTC_P0100

logger = logging.getLogger(__name__)

stations_def = [
    ('11359201', {'name': u'Brno, botanical garden PřF MU', 'geometry': GEOSGeometry('POINT (1847520.94 6309563.27)', srid=3857)}),
    ('11359196', {'name': u'Brno, Kraví Hora', 'geometry': GEOSGeometry('POINT (1846146.81 6309747.11)', srid=3857)}),
    ('11359205', {'name': u'Brno, FF MU, Arne Nováka', 'geometry': GEOSGeometry('POINT (1847675.56 6308956.40)', srid=3857)}),
    ('11359192', {'name': u'Brno, Schodová', 'geometry': GEOSGeometry('POINT (1849450.89 6310106.96)', srid=3857)}),
    ('11359202', {'name': u'Brno, Hroznová', 'geometry': GEOSGeometry('POINT (1844818.10 6307765.97)', srid=3857)}),
    ('11359132', {'name': u'Brno, Mendlovo nám.', 'geometry': GEOSGeometry('POINT (1847158.39 6307383.04)', srid=3857)}),
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


# 6 prop * 6 per hour * 4 st = 144
# 9 prop * 4 per hour * 1 st =  36
# 4 prop * 6 per hour * 1 st =  24
# TOTAL 204 per hour * 24 = 4896 per day
def count_observations(day, aggregated = False):
    time_from = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC_P0100)
    time_to = day + timedelta(days=1)
    time_range_boundary = '[]' if time_from == time_to else '[)'
    pt_range = DateTimeTZRange(time_from, time_to, time_range_boundary)

    measure_process_id = ['measure']
    aggregated_process_id = ["avg_hour", "avg_day", "apps.common.aggregate.arithmetic_mean", "apps.common.aggregate.circle_mean", "apps.common.aggregate.sum_total"]

    process_ids = measure_process_id
    if aggregated:
        process_ids = aggregated_process_id

    process = Process.objects.filter(name_id__in=process_ids)

    return Observation.objects.filter(
        phenomenon_time_range__contained_by=pt_range,
        feature_of_interest__id_by_provider__in=[station[0] for station in stations_def],
        procedure__in=process,
    ).count()


def get_or_create_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'id_by_provider')


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
                pt_range = DateTimeTZRange(
                    time_from, time_to, time_range_boundary)
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
                        logger.error(e)
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
