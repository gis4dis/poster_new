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
import pytz

class Command(BaseCommand):
    help = 'Create EventObservation from ProviderLog'

    def handle(self, *args, **options):
        observed_property = "occuring_events"
        procedure = "observation"

        # EventObservation.objects.all().delete()
        # raise Exception('DONE')
        
        # get whole extent for feature_of_interest
        admin_units = AdminUnit.objects.all().order_by('id_by_provider')
        units_list = []
        for admin_unit in admin_units:
            units_list.append(admin_unit)
        
        event_extents = EventExtent.objects.all()
        whole_extent = None
    
        for extent in event_extents:
            extent_admin = []
            for adm in extent.admin_units.order_by('id_by_provider').all():
                extent_admin.append(adm)
            if(extent_admin == units_list):
                whole_extent = extent
                break
        
        # get IDs to prevent duplicates
        ids= []
        for event in EventObservation.objects.iterator():
            ids.append(event.id_by_provider)
        
        i = 0
        for event in ProviderLog.objects.iterator():

            data = event.body
            tree = ET.fromstring(data)

            for msg in tree.iter('MSG'):
                codes = []
                category = ""
                dt_range = None
                id_by_provider = ""

                id_by_provider = msg.attrib['id']

                if(id_by_provider in ids):
                    print('Event already in database: {}'.format(id_by_provider))
                    continue
            
                ids.append(id_by_provider)
                
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
                        
                if(len(codes) == 0):
                    continue

                for cat in msg.iter('EVI'):
                    category = cat.attrib["eventcode"]  
                    break
                for tag in msg.iter('TSTA'):
                    start_time = parse(tag.text)
                for tag in msg.iter('TSTO'):
                    end_time = parse(tag.text)
                
                
                start_time = start_time.astimezone(UTC_P0100) 
                end_time = end_time.astimezone(UTC_P0100)
                if(end_time < start_time):
                    start_time, end_time = end_time, start_time

                dt_range = DateTimeTZRange(start_time, end_time)

                
                if(len(codes) > 0):
                    admin_units = AdminUnit.objects.filter(id_by_provider__in=codes)
                    units_list = []
                    for admin_unit in admin_units:
                        units_list.append(admin_unit)
                        
                    event_extents = EventExtent.objects.filter(admin_units__in=admin_units).order_by('admin_units')
                    event_extent = None
                    
                    for extent in event_extents:
                        extent_admin = []
                        for adm in extent.admin_units.all():
                            extent_admin.append(adm)
                        if(extent_admin == units_list):
                            event_extent = extent
                            break

                    event_category = EventCategory.objects.filter(id_by_provider=category).get()
                    observation = EventObservation(
                        phenomenon_time_range= dt_range,
                        observed_property=Property.objects.filter(name_id=observed_property).get(),
                        feature_of_interest=whole_extent,
                        procedure=Process.objects.filter(name_id=procedure).get(),
                        category=event_category,
                        id_by_provider=id_by_provider,
                        result=event_extent)
                    observation.save()
                    i += 1
                    print('Number of new events: {}'.format(i))

        print('Number of new events: {}'.format(i))
        # print('Extents in database: {}'.format(extents))
        
