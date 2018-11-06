from django.test import TestCase
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, EventCategory, CategoryCustomGroup, NumberOfEventsObservation
from apps.importing.models import ProviderLog, Provider
from apps.common.models import Property, Process
from django.contrib.gis.geos import GEOSGeometry, Point
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime, date
from apps.processing.rsd.management.commands.import_events import import_events
from apps.processing.rsd.management.commands.import_extents import import_extents
from apps.processing.rsd.management.commands.import_towns import import_towns
from apps.processing.rsd.management.commands.import_categories import import_categories
from apps.processing.rsd.management.commands.import_number_of_events import import_number_of_events
from apps.processing.rsd.testing.provider_logs import import_provider_logs
import pytz
from apps.utils.test_util import copy_test_files

# ./dcmanage.sh test
# ./dcmanage.sh test apps.processing.rsd.tests.ImportEventsTestCase.test_number_of_events

day_from = date(2018, 3, 23)
day_to = date(2018, 3, 24)


def import_events_test():
    provider_logs = ProviderLog.objects.all()
    return import_events(
        provider_logs=provider_logs,
        day_from=day_from,
        day_to=day_to
    )


class ImportEventsTestCase(TestCase):
    def setUp(self):
        copy_test_files()

        import_towns('test/apps.processing.rsd/obce_4326_vyber.shp')
        import_towns('test/apps.processing.rsd/momc_4326_vyber.shp')

        process = Process.objects.create(
            name_id='observation',
            name='observation'
        )

        prop = Property.objects.create(
            name_id='occuring_events',
            name='occuring events',
            unit=''
        )

        prop2 = Property.objects.create(
            name_id="number_of_emerged_events",
            name="number of emerged events",
            unit=''
        )

        provider = Provider.objects.create(
            name='Ředitelství silnic a dálnic',
            code='rsd',
            token='847da63c-fc46-4c15-88d8-c8094128d1d8'
        )

        import_provider_logs(provider)

        import_categories(day_from, day_to)

        EventExtent.objects.create(
            name_id="brno_brno_venkov_d1"
        )
        import_extents(day_from, day_to)
        import_events_test()

    def test_outside_extent(self):
        # log_outside_extent not imported
        self.assertEqual(EventExtent.objects.filter(
            admin_units__name__in=["Znojmo"]).exists(), False)
        self.assertEqual(EventObservation.objects.filter(
            id_by_provider="6f17839b-9ffe-4cfd-9b56-87346778841e").exists(), False)

    def test_categories(self):
        # categories from log_1 exists
        self.assertEqual(EventCategory.objects.filter(
            id_by_provider="401").exists(), True)
        self.assertEqual(EventCategory.objects.filter(
            id_by_provider="704").exists(), True)
        self.assertEqual(EventCategory.objects.all().count(), 2)

    def test_special_extent(self):
         # special extent has all admin units from imported events
        self.assertEqual(EventExtent.objects.filter(name_id="brno_brno_venkov_d1",
                                                    admin_units__id_by_provider__in=['583600', '583251']).exists(),
                         True)
        self.assertEqual(EventCategory.objects.all().count(), 2)

    def test_time_transformation(self):
        # check time transform to utc + 1 for log_1.xml
        imported_time = EventObservation.objects.get(
            id_by_provider="6f17839b-9ffe-4cfd-9b56-87346778841d").phenomenon_time_range

        timezone = pytz.utc
        expected_time = DateTimeTZRange(
            datetime(2018, 3, 25, 22, 0, tzinfo=timezone),
            datetime(2018, 5, 24, 22, 0, tzinfo=timezone)
        )

        self.assertEqual(imported_time, expected_time)

    def test_number_of_events(self):
        # check import number of events
        custom_401 = CategoryCustomGroup.objects.create(
            name_id='cat_401',
            name='dopravni uzavirky',
        )
        custom_704 = CategoryCustomGroup.objects.create(
            name_id='cat_704',
            name='prace na silnici',
        )
        cat_401 = EventCategory.objects.filter(
            id_by_provider="401")

        cat_704 = EventCategory.objects.filter(
            id_by_provider="704")

        cat_401.update(custom_group=custom_401)
        cat_704.update(custom_group=custom_704)

        day_from = datetime(2018, 3, 25, 0, 0, tzinfo=pytz.utc)
        day_to = datetime(2018, 3, 26, 0, 0, tzinfo=pytz.utc)

        import_number_of_events(day_from, day_to)

        self.assertEqual(
            NumberOfEventsObservation.objects.count(),
            96
        )

        NumberOfEventsObservations = []
        for event in NumberOfEventsObservation.objects.all().iterator():
            if(event.result > 0):
                NumberOfEventsObservations.append(event)

        time_from = datetime(2018, 3, 25, 21, 0, tzinfo=pytz.utc)
        time_to = datetime(2018, 3, 25, 22, 0, tzinfo=pytz.utc)

        self.assertEqual(
            NumberOfEventsObservations[0].phenomenon_time_range,
            DateTimeTZRange(time_from, time_to)
        )

        self.assertEqual(
            NumberOfEventsObservations[0].category_custom_group,
            custom_401
        )
