from django.test import TestCase
from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry, Point
from apps.common.models import Process, Property
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from apps.ad.anomaly_detection import get_timeseries

time_range_boundary = '[)'
time_from = datetime(2018, 6, 15, 00, 00, 00)
date_time_range = DateTimeTZRange(
    time_from,
    time_from + timedelta(hours=24),
    time_range_boundary
)

def get_time_series_test():
    station = SamplingFeature.objects.get(name="Brno")
    prop = Property.objects.get(name_id='air_temperature')
    time_range = date_time_range

    return get_timeseries(
        observed_property=prop,
        observation_provider_model=Observation,
        feature_of_interest=station,
        phenomenon_time_range=time_range
    )


# TODO create ticket - describe problem, ask for a fix (test with this TimeSeriesTestCase), hangout
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

        at_prop = Property.objects.create(
            name_id='air_temperature',
            name='air temperature',
            unit='°C',
            default_mean=am_process
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

    def test_get_time_series_property_values(self):
        ts = get_time_series_test()
        self.assertEqual(ts['property_values'], [1.000])
