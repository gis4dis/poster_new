from django.db import models
from apps.importing.models import ProviderLog
from apps.common.models import Property, Process
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, EventCategory
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from psycopg2.extras import DateTimeTZRange
from apps.utils.time import UTC_P0100
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta, tz

class Command(BaseCommand):
    help = 'Create events from ProviderLog'

    def handle(self, *args, **options):
        i = 0
        observed_property = "Occuring events"
        procedure = "Observation"
        # ProviderLog.objects.all().delete()
        for event in ProviderLog.objects.iterator():
            i += 1
            if(i == 30):
                break

            data = event.body
            tree = ET.fromstring(data)

            codes = []
            category = ""
            dt_range = None
            id_by_provider = ""

            for tag in tree.iter('DEST'):
                road = tag.find('ROAD')
                is_d1 = False
                if road is not None and 'RoadNumber' in road.attrib:
                    is_d1 = True if road.attrib['RoadNumber'] == 'D1' else False
                town_ship = tag.attrib['TownShip']
                if((town_ship == 'Brno-venkov' or town_ship == 'Brno') or (is_d1)):
                    code = tag.attrib['TownCode']
                    codes.append(code)
                    for cat in tree.iter('TXUCL'):
                        category = cat.text
                        break

                    for tag in tree.iter('TSTA'):
                        start_time = parse(tag.text)
                    for tag in tree.iter('TSTO'):
                        end_time = parse(tag.text)

                    start_time.replace(tzinfo=UTC_P0100)
                    end_time.replace(tzinfo=UTC_P0100)
                    dt_range = DateTimeTZRange(start_time, end_time)

                    for tag in tree.iter('MSG'):
                        id_by_provider = tag.attrib['id']

                    admin_units = (AdminUnit.objects.filter(id_by_provider__in=codes))
                    event_extent = EventExtent.objects.filter(admin_units__in=admin_units)
                    # event_extent = EventExtent.admin_units
                    event_category = EventCategory.objects.filter(name=category).get()

                    observation = EventObservation(
                        phenomenon_time_range= dt_range,
                        observed_property=Property.objects.filter(name=observed_property).get(),
                        feature_of_interest=event_extent,
                        procedure=Process.objects.filter(name=procedure).get(),
                        category=event_category,
                        id_by_provider=id_by_provider,
                        result=event_extent)
                    observation.save()

            
        # print('Extents in database: {}'.format(extents))
        
