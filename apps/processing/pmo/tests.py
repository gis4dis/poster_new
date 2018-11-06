from django.test import TestCase
from apps.common.models import Process, Property
from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.pmo.models import WeatherStation, WeatherObservation
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime, date
from apps.processing.pmo.management.commands.pmo_srazsae_import import srazsae_import
import pytz
from apps.utils.test_util import copy_test_files

# ./dcmanage.sh test apps.processing.pmo

class SrazsaeImportTestCase(TestCase):
    def setUp(self):
        copy_test_files()
        path = "/test/apps.processing.pmo/"
        day_from = datetime(2017, 11, 24)
        day_to = datetime(2017, 11, 25)
        srazsae_import(path, day_from, day_to)

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
