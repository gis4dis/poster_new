from django.test import TestCase
from apps.processing.pmo.models import WeatherStation, WeatherObservation
from psycopg2.extras import DateTimeTZRange
from datetime import datetime
import pytz
from apps.utils.test_util import copy_test_files
from apps.processing.pmo.util import util


# ./dcmanage.sh test apps.processing.pmo
class SrazsaeImportTestCase(TestCase):
    def setUp(self):
        copy_test_files()

        WeatherStation.objects.create(
            id_by_provider='001',
            name='',
            geometry=None,
            basin=''
        )

        date = datetime(2017, 11, 24)
        util.load_srazsae(date, "/test/apps.processing.pmo/")

    def test_srazsae_import(self):
        # check import number of observations
        self.assertEqual(
            WeatherObservation.objects.count(),
            10
        )

        # check phenomenon_time_range of 1st observation
        imported_time = WeatherObservation.objects.order_by(
            "phenomenon_time_range")[0].phenomenon_time_range
        timezone = pytz.utc
        expected_time = DateTimeTZRange(
            datetime(2017, 11, 16, 9, 0, tzinfo=timezone),
            datetime(2017, 11, 16, 9, 0, tzinfo=timezone),
            '[]')

        self.assertEqual(imported_time, expected_time)
