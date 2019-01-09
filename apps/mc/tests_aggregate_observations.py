from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry
from apps.common.models import Process
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta
from django.db.models import F, Func
from django.utils.dateparse import parse_datetime
from django.test import TestCase

from apps.common.models import Property
import pytz
from apps.mc.tasks import compute_aggregated_values

utc = pytz.UTC

STATION_PROPS = {
    '11359201': {
        'id_by_provider': '11359201',
        'geom_type': 'Point',
        'name': 'Brno',
        'coordinates': [1847520.94, 6309563.27]
    }
}

time_range_boundary = '[)'

def create_station(key):
    station_key = key
    props = STATION_PROPS[station_key]
    coordinates = props['coordinates']
    return SamplingFeature.objects.create(
        id_by_provider=props['id_by_provider'],
        name=props['name'],
        geometry=GEOSGeometry(
            props['geom_type'] + ' (' + str(coordinates[0]) + ' ' + str(coordinates[1]) + ')',
            srid=3857
        )
    )


VALUES_28_9_2018 = [9.0, 9.0, 9.0, 9.1, 9.1, 9.1, 9.1, 9.1, 9.2, 9.1, 9.3, 9.3, 9.3, 9.2, 9.1, 9.1, 9.2, 9.2]
AGG_VALUES_28_2018 = [9.050, 9.183, 9.183]
DATETIME_28_2018 = parse_datetime('2018-10-28T00:00:00+01:00')

VALUES_29_9_2018 = [9.000, 9.000, 9.000, 9.100, 9.100, 9.100, 9.100, 9.100, 9.200, 9.100, 9.300, 9.300, 9.300, 9.200, 9.100, 9.100, 9.200, 9.200, 9.300, 9.300, 9.300, 9.200, 9.200, 9.300, 9.300, 9.300, 9.400, 9.500, 9.500, 9.500, 9.300, 9.300, 9.300, 9.400, 9.400, 9.400, 9.500, 9.500, 9.600, 9.700, 9.800, 9.800, 10.000, 10.200, 10.300, 10.300, 10.000, 10.000, 9.800, 10.000, 10.100, 10.200, 10.300, 10.500, 10.600, 10.800, 11.000, 11.100, 11.300, 11.400, 11.500, 11.600, 11.700, 11.900, 12.100, 12.300, 12.500, 12.700, 13.000, 13.500, 14.200, 15.300, 14.900, 14.800, 15.100, 14.900, 15.500, 15.500, 15.500, 15.300, 15.500, 16.500, 17.000, 17.000, 17.100, 17.500, 17.500, 17.600, 17.600, 17.600, 17.500, 17.400, 17.300, 17.400, 17.300, 17.000, 17.000, 17.000, 17.000, 17.000, 17.000, 17.200, 17.300, 17.400, 17.300, 17.400, 17.500, 17.600, 17.700, 17.800, 17.800, 17.800, 18.000, 18.100, 17.800, 18.100, 18.000, 17.800, 17.600, 17.700, 17.900, 17.800, 17.800, 17.900, 17.700, 17.800, 17.900, 17.800, 17.600, 17.700, 17.500, 17.400, 17.500, 17.500, 17.500, 17.500, 17.400, 17.600, 17.300, 17.200, 17.300, 17.200, 17.300, 17.500]
AGG_VALUES_29_2018 = [9.050, 9.183, 9.183, 9.267, 9.417, 9.350, 9.650, 10.133, 10.150, 11.033, 11.850, 13.533, 15.117, 16.133, 17.483, 17.317, 17.033, 17.417, 17.867, 17.833, 17.817, 17.650, 17.500, 17.300]
DATETIME_29_2018 = parse_datetime('2018-10-29T00:00:00+01:00')


def createObservations(
    measuring_process,
    station,
    prop,
    values,
    start
):
    time_range_boundary = '[]'
    time_from = start
    for val in values:
        Observation.objects.create(
            observed_property=prop,
            feature_of_interest=station,
            procedure=measuring_process,
            result=val,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from,
                time_range_boundary
            )
        )
        time_from = time_from + timedelta(minutes=10)



class AggregateObservationsTestCase(TestCase):
    def setUp(self):
        am_process = Process.objects.create(
            name_id='apps.common.aggregate.arithmetic_mean',
            name='arithmetic mean'
        )

        measuring_process = Process.objects.create(
            name_id='measure',
            name='measuring'
        )

        station_key = '11359201'
        station = create_station(station_key)

        at_prop = Property.objects.create(
            name_id='air_temperature',
            name='air temperature',
            unit='°C',
            default_mean=am_process
        )

        Property.objects.create(
            name_id='ground_air_temperature',
            name='ground_air_temperature',
            unit='°C',
            default_mean=am_process
        )

        Property.objects.create(
            name_id='precipitation',
            name='precipitation',
            unit='mm',
            default_mean=am_process
        )

        createObservations(
            measuring_process,
            station,
            at_prop,
            VALUES_28_9_2018,
            DATETIME_28_2018
        )

    def test_initial_aggregation(self):
        compute_aggregated_values(None)

        agg_obs = Observation.objects.filter(
            procedure=Process.objects.get(name_id='apps.common.aggregate.arithmetic_mean')
        ).annotate(
            field_lower=Func(F('phenomenon_time_range'), function='LOWER')
        ).order_by('field_lower')

        result_list = [float(entry.result) for entry in agg_obs]

        self.assertEqual(result_list, AGG_VALUES_28_2018)

    def test_additional_import(self):
        createObservations(
            Process.objects.get(name_id='measure'),
            SamplingFeature.objects.get(id_by_provider='11359201'),
            Property.objects.get(name_id='air_temperature'),
            VALUES_29_9_2018,
            DATETIME_29_2018
        )

        compute_aggregated_values(None)

        agg_obs = Observation.objects.filter(
            procedure=Process.objects.get(name_id='apps.common.aggregate.arithmetic_mean')
        ).annotate(
            field_lower=Func(F('phenomenon_time_range'), function='LOWER')
        ).order_by('field_lower')

        result_list = [float(entry.result) for entry in agg_obs]

        self.assertEqual(result_list, AGG_VALUES_28_2018 + AGG_VALUES_29_2018)