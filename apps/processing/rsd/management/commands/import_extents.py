from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventExtent, AdminUnit
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET

class Command(BaseCommand):
    help = 'Create extents from events'

    def handle(self, *args, **options):
        extents = []
        i = 0
        # EventExtent.objects.all().delete()
        for ext in EventExtent.objects.all():
            extent = list(ext.admin_units.all().order_by('id_by_provider'))
            extents.append(extent)
        for event in ProviderLog.objects.iterator():
            event_extent = []
            codes = []
            data = event.body
            tree = ET.fromstring(data)
            for tag in tree.iter('DEST'):
                road = tag.find('ROAD')
                is_d1 = False
                if road is not None and 'RoadNumber' in road.attrib:
                    is_d1 = True if road.attrib['RoadNumber'] == 'D1' else False
                town_ship = tag.attrib['TownShip']
                if((town_ship == 'Brno-venkov' or town_ship == 'Brno') or (is_d1)):
                    code = tag.attrib['TownCode']
                    codes.append(code)

            event_extent = list(AdminUnit.objects.filter(id_by_provider__in=codes).order_by('id_by_provider'))
            if not event_extent in extents and len(event_extent) > 0:
                extents.append(event_extent)
                ext = EventExtent()
                ext.save()
                i += 1
                for code in codes:
                    unit = AdminUnit.objects.filter(id_by_provider=code).get()
                    ext.admin_units.add(unit)
                
        # print('Extents in database: {}'.format(extents))
        print('Number of extents: {}'.format(len(extents)))
        print('Number of new extents: {}'.format(i)
        
