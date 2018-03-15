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

# ./dcmanage.sh show_events --geometry 'POINT(16.597252 49.157379)' --categories ['Práce na silnici','Nehoda'] --time_range_start "1 1 2018 12:00" --time_range_end "28 1 2018 20:00" --buffer 10000




    def add_arguments(self, parser):
        parser.add_argument('--geometry', nargs='?', type=str,
                            default=None)
        parser.add_argument('--categories', nargs='?', type=list,
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
        if geom is None:
            raise Exception("No geometry defined!")
        else:
            geom = GEOSGeometry(geom, srid=4326)
            geom = geom.transform(3857,clone=True)
        categories = []
        if categories_param is None:
            raise Exception("No event categories defined!")
        else:
            text = ''
            for category in categories_param:
                if(category == '['):
                    continue
                if(category == ']'):
                    categories.append(text)
                    continue
                if(category == ','):
                    categories.append(text)
                    text = ''
                    continue
                text += category

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
        for event in EventObservation.objects.iterator():
            is_geometry = False
            is_category = False
            is_time = False
            
            for category in categories:
                if(category == event.category.name):
                    is_category = True
            if(not is_category):
                continue

            start_time = event.phenomenon_time_range.lower
            end_time = event.phenomenon_time_range.upper

            is_time = time_in_range(start_time, end_time, start_range, end_range)
            if(not is_time):
                continue

            for admin_unit in event.result.admin_units.iterator():
                if(admin_unit.geometry.intersects(geom_final)):
                    is_geometry = True
                    # print('Intersected: {}'.format(admin_unit))

            if(is_geometry):
                i += 1
                print('Number of EventObservations: {}'.format(i))
                result.append(event)
        print('Result: {}'.format(result))

def time_in_range(start, end, day_start, day_end):
    """Return true if event time range overlaps time range in argument"""
    if (start <= day_start and end >= day_end):
        return True
    elif (start >= day_start and start <= day_end):
        return True
    elif (end >= day_start and end <= day_end):
        return True
    return False

            