from django.test import TestCase
from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry, Point
from apps.common.models import Process, Property
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from apps.ad.anomaly_detection import get_timeseries


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
date_time_range = DateTimeTZRange(
    time_from,
    time_from + timedelta(hours=24),
    time_range_boundary
)


def get_time_series_test():
    station = SamplingFeature.objects.get(name="Brno2")
    prop = Property.objects.get(name_id='air_temperature')
    time_range = date_time_range

    return get_timeseries(
        observed_property=prop,
        observation_provider_model=Observation,
        feature_of_interest=station,
        phenomenon_time_range=time_range
    )


# TODO create ticket - describe problem, ask for a fix (test with this TimeSeriesTestCase), hangout
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

        time_from = datetime(2018, 6, 15, 11, 00, 00)
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

        time_from = datetime(2018, 6, 15, 10, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 15, 11, 00, 00)
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

        time_from = datetime(2018, 6, 15, 12, 00, 00)
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


    #TODO otestovat ruzne vstupy a spravne vystupy - i mezni pripady (prazdna data)
    #TODO empty if no observations were found, None if no observations were found, missing result
    #  is represented by None in the list, empty list if no observations were found
    #TODO otherwise it's [ beginning of the first observation, beginning of the last observation + value frequency )

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

    def test_get_time_series_property_values(self):
        ts = get_time_series_test()
        self.assertEqual(ts['property_values'], [1.000, 1000.000, 1.500])

    def test_get_time_series_count(self):
        ts = get_time_series_test()
        self.assertEqual(len(ts['property_values']), 3)

    def test_property_values_count_equal_anomaly_rates_count(self):
        ts = get_time_series_test()
        self.assertEqual(len(ts['property_values']), len(ts['property_anomaly_rates']))

    def test_time_series_out_bounds(self):
        ts = get_time_series_test()
        lower_inc = ts['phenomenon_time_range'].lower_inc
        upper_inc = ts['phenomenon_time_range'].upper_inc
        self.assertTrue(lower_inc)
        self.assertFalse(upper_inc)

    def test_time_series_out_lower_is_multiply_of_value_frequency(self):
        ts = get_time_series_test()
        result = ts['phenomenon_time_range'].lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_time_series_out_interval_is_multiply_of_value_frequency(self):
        ts = get_time_series_test()
        lower = ts['phenomenon_time_range'].lower
        upper = ts['phenomenon_time_range'].upper
        result = upper.timestamp() - lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_time_series_time_range_in_contains_out(self):
        ts = get_time_series_test()
        out_lower = ts['phenomenon_time_range'].lower
        out_upper = ts['phenomenon_time_range'].upper
        self.assertTrue(out_lower >= date_time_range.lower)
        self.assertTrue(out_upper < date_time_range.upper)

    def test_time_series_in_bounds(self):
        ts = get_time_series_test()
        lower_inc = date_time_range.lower_inc
        upper_inc = date_time_range.upper_inc
        self.assertTrue(lower_inc)
        self.assertFalse(upper_inc)

    def test_time_series_in_lower_is_multiply_of_value_frequency(self):
        ts = get_time_series_test()
        result = date_time_range.lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_time_series_in_interval_is_multiply_of_value_frequency(self):
        ts = get_time_series_test()
        lower = date_time_range.lower
        upper = date_time_range.upper
        result = upper.timestamp() - lower.timestamp()
        f = ts['value_frequency']
        self.assertEqual(result % f, 0)

    def test_property_values_length_equals_out_range(self):
        ts = get_time_series_test()
        lower = ts['phenomenon_time_range'].lower
        upper = ts['phenomenon_time_range'].upper
        property_values_length = len(ts['property_values'])
        f = ts['value_frequency']
        estimated_length = (upper.timestamp() - lower.timestamp()) / f
        self.assertEquals(property_values_length, estimated_length)

    def test_todo(self):
        self.assertEquals(True, False)
        #otestovat time range, ze output odpovida zacatku v predpokladanych datech a konec je za
        # poslednim merenim + value frequency
