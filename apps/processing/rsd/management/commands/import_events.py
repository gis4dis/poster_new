from django.db import models
from apps.importing.models import ProviderLog
from apps.common.models import Property, Process
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, EventCategory
from apps.processing.rsd.management.commands.import_categories import parse_date
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from psycopg2.extras import DateTimeTZRange
from apps.utils.time import UTC_P0100
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta, tz
import pytz
from django.contrib.gis.geos import GEOSGeometry, Point

class Command(BaseCommand):
    help = 'Create EventObservation from ProviderLog. If no arguments - takes data from yesterday ' \
    './dcmanage.sh import_events --date_from=2018-01-01 --date_to=2018-01-01'

    def add_arguments(self, parser):
        parser.add_argument('--date_from', nargs='?', type=str,
                            default=None)
        parser.add_argument('--date_to', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        
        # EventObservation.objects.all().delete()

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
        import_events(ProviderLog.objects.all(), day_from, day_to)

def import_events(provider_logs, day_from, day_to):
    observed_property = "occuring_events"
    procedure = "observation"
    new_observations = []
    # get whole extent for feature_of_interest
    admin_units = AdminUnit.objects.all().order_by('id_by_provider')
    units_list = []
    for admin_unit in admin_units:
        units_list.append(admin_unit)
    
    event_extents = EventExtent.objects.all()
    
    # extent of d1, brno, brno venkov admin units
    whole_extent = get_special_extent()
    whole_extent_units = list(whole_extent.admin_units.all())
    
    # get IDs to prevent duplicates
    ids= []
    for event in EventObservation.objects.iterator():
        ids.append(event.id_by_provider)
    
    i = 0
    for provider_log in provider_logs.filter(received_time__range=(day_from, day_to)).iterator():

        data = provider_log.body
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

            for tag in msg.iter('COORD'):
                coord_x = tag.attrib['x']
                coord_y = tag.attrib['y']
            
            geom = Point(float(coord_y), float(coord_x))
            if geom is not None:
                geom = GEOSGeometry(geom, srid=4326)
                geom = geom.transform(3857, clone=True)
            
            if(len(codes) > 0):
                admin_units = AdminUnit.objects.filter(id_by_provider__in=codes)
                units_list = []
                for admin_unit in admin_units:
                    units_list.append(admin_unit)
                    if(not admin_unit in whole_extent_units):
                        whole_extent.admin_units.add(admin_unit)
                        whole_extent_units.append(admin_unit)
                    
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
                    result=event_extent,
                    point_geometry=geom,
                    provider_log=provider_log,
                )
                observation.save()
                new_observations.append(observation)
                i += 1
                print('Number of new events: {}'.format(i))

    print('Number of new events: {}'.format(i))
    # print('Extents in database: {}'.format(extents))
    return new_observations
        

def get_special_extent():
    ext = EventExtent.objects.get(name_id="brno_brno_venkov_d1")
    if ext:
        return ext
    else:
        ext = EventExtent(name_id="brno_brno_venkov_d1")
        ext.save()
        return ext