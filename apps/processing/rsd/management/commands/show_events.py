from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, EventCategory
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from apps.utils.time import UTC_P0100

from psycopg2.extras import DateTimeTZRange
from django.contrib.gis.geos import GEOSGeometry


class Command(BaseCommand):
    help = 'Find unique events of given categories that' \
            'occur at given time range and in given spatial extent.'

# ./dcmanage.sh show_events --geometry 'POINT(16.597252 49.157379)' --categories '201, 211' --time_range_start "1 1 2018 12:00" --time_range_end "28 1 2018 20:00" --buffer 10000

    def add_arguments(self, parser):
        parser.add_argument('--geometry', nargs='?', type=str,
                            default=None)
        parser.add_argument('--categories', nargs='?', type=str,
                            default=None)
        parser.add_argument('--time_range_start', nargs='?', type=str,
                            default=None)
        parser.add_argument('--time_range_end', nargs='?', type=str,
                            default=None)
        parser.add_argument('--buffer', nargs='?', type=float,
                            default=None)

    def handle(self, *args, **options):
        geom = options['geometry']
        categories_param = options['categories']
        time_range_start = options['time_range_start']
        time_range_end = options['time_range_end']
        buffer = options['buffer']
        findEvents(geom, categories_param, time_range_start, time_range_end, buffer)


def findEvents(geom, categories_param, time_range_start, time_range_end, buffer):
    if geom is None:
        raise Exception("No geometry defined!")
    else:
        geom = GEOSGeometry(geom, srid=4326)
        geom = geom.transform(3857,clone=True)
    categories = []
    if categories_param is None:
        raise Exception("No event categories defined!")
    else:
        categories = categories_param.split(",")   
    if time_range_start is None or time_range_end is None:
        raise Exception("No time range defined!")
    else:
        start_range = parse(time_range_start)
        end_range = parse(time_range_end)
        if(start_range.tzinfo is None or start_range.tzinfo.utcoffset(start_range) is None):
            
            start_range = start_range.replace(tzinfo=UTC_P0100)
        if(end_range.tzinfo is None or end_range.tzinfo.utcoffset(end_range) is None):
            end_range = end_range.replace(tzinfo=UTC_P0100)
        if(start_range.tzinfo != UTC_P0100):
            start_range = start_range.astimezone(UTC_P0100)
        if(end_range.tzinfo != UTC_P0100):
            end_range = end_range.astimezone(UTC_P0100)

    if buffer is None:
        raise Exception("No buffer defined!")
    else:
        buffer = buffer

    geom_final = geom.buffer(buffer)

    i = 0
    result = []
    pt_range = DateTimeTZRange(start_range, end_range)
    evt_obj = EventObservation.objects.filter(
        phenomenon_time_range__overlap=pt_range,
        category__id_by_provider__in=categories
        )
    
    for event in evt_obj:
        is_geometry = False

        for admin_unit in event.result.admin_units.iterator():
            if(admin_unit.geometry.intersects(geom_final)):
                is_geometry = True
                # print('Intersected: {}'.format(admin_unit))

        if(is_geometry):
            i += 1
            print('Number of EventObservations: {}'.format(i))
            result.append(event)
    print('Result: {}'.format(result))

            
