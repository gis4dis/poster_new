from django.test import TestCase
from apps.processing.ala.models import SamplingFeature, Observation
from apps.processing.o2.models import MobilityObservation
from django.contrib.gis.geos import GEOSGeometry, Point
from apps.common.models import Process, Property
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from apps.ad.anomaly_detection import get_timeseries
from apps.utils.time import UTC_P0100

'''
    Example result of get_timeseries:
    {
        'phenomenon_time_range': DateTimeTZRange(datetime.datetime(2018, 6, 15, 11, 0), datetime.datetime(2018, 6, 15, 14, 0), '[)'), 
        'value_frequency': 3600, 
        'property_values': [
            Decimal('1.000'), 
            Decimal('1000.000'), 
            Decimal('1.500')
        ], 
        'property_anomaly_rates': [
            0.0, 
            1.697480910372832, 
            0.9625824050649426
        ]
    }

'''

time_range_boundary = '[)'
time_from = datetime(2018, 6, 15, 00, 00, 00)
time_from = time_from.replace(tzinfo=UTC_P0100)
date_time_range = DateTimeTZRange(
    time_from,
    time_from + timedelta(hours=24),
    time_range_boundary
)

time_from_no_data = datetime(2018, 9, 15, 00, 00, 00)
time_from_no_data = time_from_no_data.replace(tzinfo=UTC_P0100)
date_time_range_no_data = DateTimeTZRange(
    time_from_no_data,
    time_from_no_data + timedelta(hours=24),
    time_range_boundary
)

observation_from = datetime(2018, 6, 15, 10, 00, 00)
observation_from = observation_from.replace(tzinfo=UTC_P0100)
first_output_observation_time_range = DateTimeTZRange(
    observation_from,
    observation_from + timedelta(hours=1),
    time_range_boundary
)

observation_from = datetime(2018, 6, 15, 12, 00, 00)
observation_from = observation_from.replace(tzinfo=UTC_P0100)
last_output_observation_time_range = DateTimeTZRange(
    observation_from,
    observation_from + timedelta(hours=1),
    time_range_boundary
)


def get_time_series_test(
        stationName,
        time_range,
        observed_property="air_temperature",
        observation_provider_model=Observation):

    station = SamplingFeature.objects.get(name=stationName)
    prop = Property.objects.get(name_id=observed_property)
    return get_timeseries(
        observed_property=prop,
        observation_provider_model=observation_provider_model,
        feature_of_interest=station,
        phenomenon_time_range=time_range
    )

# TODO udelat nejak inteligentni zakladani setup
# TODO readme - jak se pousti testy
# ./dcmanage.sh test
# ./dcmanage.sh test apps.mc
# ./dcmanage.sh test apps.mc.tests.TimeSeriesTestCase
# ./dcmanage.sh test apps.mc.tests.TimeSeriesTestCase.test_properties_response_status


class TimeSeriesTestCase(TestCase):
    def setUp(self):
        am_process = Process.objects.create(
            name_id='apps.common.aggregate.arithmetic_mean',
            name='arithmetic mean'
        )

        station = SamplingFeature.objects.create(
            id_by_provider="11359201",
            name="Brno",
            geometry=GEOSGeometry('POINT (1847520.94 6309563.27)', srid=3857)
        )

        station_2 = SamplingFeature.objects.create(
            id_by_provider="brno2_id_by_provider",
            name="Brno2",
            geometry=GEOSGeometry('POINT (1847520.94 6309563.27)', srid=3857)
        )

        at_prop = Property.objects.create(
            name_id='air_temperature',
            name='air temperature',
            unit='°C',
            default_mean=am_process
        )

        Property.objects.create(
            name_id='water_level',
            name='water level',
            unit='cm',
            default_mean=am_process
        )

        time_from = datetime(2018, 6, 15, 11, 00, 00)
        time_from = time_from.replace(tzinfo=UTC_P0100)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 15, 12, 00, 00)
        time_from = time_from.replace(tzinfo=UTC_P0100)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 14, 13, 00, 00)
        time_from = time_from.replace(tzinfo=UTC_P0100)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1,
            phenomenon_time_range=first_output_observation_time_range
        )

        time_from = datetime(2018, 6, 15, 11, 00, 00)
        time_from = time_from.replace(tzinfo=UTC_P0100)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1000,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=last_output_observation_time_range
        )

        time_from = datetime(2018, 6, 16, 13, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

    def test_create_process(self):
        process = Process.objects.all()
        self.assertGreater(len(process), 0)

    def test_create_property(self):
        property = Property.objects.all()
        self.assertGreater(len(property), 0)

    def test_create_observation(self):
        observation = Observation.objects.all()
        self.assertGreater(len(observation), 0)

    def test_create_station(self):
        station = SamplingFeature.objects.get(name="Brno")
        self.assertEqual(station.name, 'Brno')

    def test_property_values(self):
        ts = get_time_series_test('Brno', date_time_range)
        self.assertEqual(ts['property_values'], [1.000, 1000.000, 1.500])

    def test_property_not_exists(self):
        ts = get_timeseries(
            observed_property=Property.objects.get(name_id='water_level'),
            observation_provider_model=Observation,
            feature_of_interest=SamplingFeature.objects.get(name='Brno'),
            phenomenon_time_range=date_time_range
        )
        self.assertIsNone(ts['phenomenon_time_range'].lower)
        self.assertIsNone(ts['phenomenon_time_range'].upper)
        self.assertIsNone(ts['value_frequency'])
        self.assertEqual(len(ts['property_values']), 0)
        self.assertEqual(len(ts['property_anomaly_rates']), 0)

    def test_empty_property_values(self):
        ts = get_time_series_test('Brno', date_time_range_no_data)
        self.assertIsNone(ts['phenomenon_time_range'].lower)
        self.assertIsNone(ts['phenomenon_time_range'].upper)
        self.assertIsNone(ts['value_frequency'])
        self.assertEqual(len(ts['property_values']), 0)
        self.assertEqual(len(ts['property_anomaly_rates']), 0)

    def test_count(self):
        ts = get_time_series_test('Brno', date_time_range)
        self.assertEqual(len(ts['property_values']), 3)

    def test_property_values_count_equal_anomaly_rates_count(self):
        ts = get_time_series_test('Brno', date_time_range)
        self.assertEqual(len(ts['property_values']), len(ts['property_anomaly_rates']))

    def test_out_bounds(self):
        ts = get_time_series_test('Brno', date_time_range)
        lower_inc = ts['phenomenon_time_range'].lower_inc
        upper_inc = ts['phenomenon_time_range'].upper_inc
        self.assertTrue(lower_inc)
        self.assertFalse(upper_inc)

    def test_out_lower_is_multiply_of_value_frequency(self):
        ts = get_time_series_test('Brno', date_time_range)
        result = ts['phenomenon_time_range'].lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_out_interval_is_multiply_of_value_frequency(self):
        ts = get_time_series_test('Brno', date_time_range)
        lower = ts['phenomenon_time_range'].lower
        upper = ts['phenomenon_time_range'].upper
        result = upper.timestamp() - lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_time_range_in_contains_out(self):
        ts = get_time_series_test('Brno', date_time_range)
        out_lower = ts['phenomenon_time_range'].lower
        out_upper = ts['phenomenon_time_range'].upper
        self.assertTrue(out_lower >= date_time_range.lower)
        self.assertTrue(out_upper < date_time_range.upper)

    def test_in_bounds(self):
        ts = get_time_series_test('Brno', date_time_range)
        lower_inc = date_time_range.lower_inc
        upper_inc = date_time_range.upper_inc
        self.assertTrue(lower_inc)
        self.assertFalse(upper_inc)

    def test_in_lower_is_multiply_of_value_frequency(self):
        ts = get_time_series_test('Brno', date_time_range)
        result = date_time_range.lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_in_interval_is_multiply_of_value_frequency(self):
        ts = get_time_series_test('Brno', date_time_range)
        lower = date_time_range.lower
        upper = date_time_range.upper
        result = upper.timestamp() - lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_property_values_length_equals_out_range(self):
        ts = get_time_series_test('Brno', date_time_range)
        lower = ts['phenomenon_time_range'].lower
        upper = ts['phenomenon_time_range'].upper
        property_values_length = len(ts['property_values'])
        f = ts['value_frequency']
        estimated_length = (upper.timestamp() - lower.timestamp()) / f
        self.assertEquals(property_values_length, estimated_length)

    # TODO time range - beginning of the first observation, beginning of the last observation + value frequency )
    def test_time_range_result_values(self):
        ts = get_time_series_test('Brno', date_time_range)
        expected_lower = first_output_observation_time_range.lower
        expected_upper = last_output_observation_time_range.upper
        result_lower = ts['phenomenon_time_range'].lower
        result_upper = ts['phenomenon_time_range'].upper
        # TODO vyresit problemy s casovou zonou - budto udelat konverzi +1 z resultu nebo upravit gettimeseries metodu asi
        print('result_lower: ', result_lower)
        print('expected_lower: ', expected_lower)
        # self.assertEquals(result_lower, expected_lower)
        # self.assertEquals(result_upper, expected_upper)
        #konec je za poslednim merenim + value frequency

    def test_time_range_no_data(self):
        print('TODO')

    # TODO test ruznych feature_of_interest
    def test_alternative_feature(self):
        print('TODO')







        '''
        print('INPUT OBSERVATION LOWER: ', first_output_observation_time_range.lower)
        print('OUTPUT LOWER: ',   ts['phenomenon_time_range'].lower)        
        {'phenomenon_time_range': DateTimeTZRange(datetime.datetime(2018, 6, 15, 11, 0),
                                                  datetime.datetime(2018, 6, 15, 14, 0), '[)'),
         'value_frequency': 3600,
         'property_values': [Decimal('1.000'), Decimal('1000.000'), Decimal('1.500')],
         'property_anomaly_rates': [0.0, 1.697480910372832, 0.9625824050649426]}
        '''
        #otestovat time range, ze output odpovida zacatku v predpokladanych datech a konec je za
        # poslednim merenim + value frequency
