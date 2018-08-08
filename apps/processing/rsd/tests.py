from django.test import TestCase
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, EventCategory
from apps.importing.models import ProviderLog, Provider
from apps.common.models import Property, Process
from django.contrib.gis.geos import GEOSGeometry, Point
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime, date
from apps.processing.rsd.management.commands.import_events import import_events
from apps.processing.rsd.management.commands.import_extents import import_extents
from apps.processing.rsd.management.commands.import_towns import import_towns
from apps.processing.rsd.management.commands.import_categories import import_categories
from apps.processing.rsd.testing.provider_logs import import_provider_logs

# ./dcmanage.sh test

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

        import_towns('shapefiles/rsd/obce_4326.shp')
        import_towns('shapefiles/rsd/momc_4326.shp')

        process = Process.objects.create(
            name_id='observation',
            name='observation'
        )

        prop = Property.objects.create(
            name_id='occuring_events',
            name='occuring events',
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

    def test_get_import_events_count(self):
        ts = import_events_test()
        self.assertEqual(len(ts), 1)
        self.assertEqual(ts[0].category.name, "uzavřeno")
