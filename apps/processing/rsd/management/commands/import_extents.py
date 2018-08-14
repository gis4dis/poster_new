from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation
from apps.processing.rsd.management.commands.import_categories import parse_date
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from apps.utils.time import UTC_P0100
from datetime import datetime, date, timedelta
from dateutil.parser import parse

class Command(BaseCommand):
    help = 'Create extents from events. If no arguments - takes data from yesterday ' \
    './dcmanage.sh import_extents --date_from=2018-01-01 --date_to=2018-01-02'

    def add_arguments(self, parser):
        parser.add_argument('--date_from', nargs='?', type=str,
                            default=None)
        parser.add_argument('--date_to', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):

        # EventObservation.objects.all().delete()
        # EventExtent.objects.all().delete()

        arg_from = options['date_from']
        arg_to = options['date_to']
        if arg_from is None and arg_to is None:
            day_from = date.today() - timedelta(1)
            day_to = day_from
            day_from = datetime.combine(day_from, datetime.min.time())
            day_to = datetime.combine(day_to, datetime.max.time())
        else:
            day_from = parse_date(arg_from, 1)
            day_to = parse_date(arg_to, 2)
        
        day_from = day_from.astimezone(UTC_P0100) 
        day_to = day_to.astimezone(UTC_P0100)
        import_extents(day_from, day_to)

def import_extents(day_from, day_to):
    extents = []
    i = 0
    op = 0
    for ext in EventExtent.objects.all():
        extent = list(ext.admin_units.all().order_by('id_by_provider'))
        extents.append(extent)

    for event in ProviderLog.objects.filter(received_time__range=(day_from, day_to)).iterator():
        op += 1
        
        data = event.body
        tree = ET.fromstring(data)
        for msg in tree.iter('MSG'):
            event_extent = []
            codes = []

            for tag in msg.iter('DEST'):
                road = tag.find('ROAD')
                is_d1 = False
                if road is not None and 'RoadNumber' in road.attrib:
                    is_d1 = True if road.attrib['RoadNumber'] == 'D1' else False
                town_ship = tag.attrib['TownShip']
                if((town_ship == 'Brno-venkov' or town_ship == 'Brno-město') or (is_d1)):
                    if('TownDistrictCode' in tag.attrib):
                        code = tag.attrib['TownDistrictCode']
                    else:
                        code = tag.attrib['TownCode']
                    codes.append(code)

            event_extent = list(AdminUnit.objects.filter(id_by_provider__in=codes).order_by('id_by_provider'))
            if not event_extent in extents and len(event_extent) > 0:
                extents.append(event_extent)
                ext = EventExtent()
                ext.save()
                i += 1
                print('New extent added: {}'.format(i))
                for code in codes:
                    unit = AdminUnit.objects.filter(id_by_provider=code).get()
                    ext.admin_units.add(unit)

    print('Number of extents: {}'.format(len(extents)))
    print('Number of new extents: {}'.format(i))

