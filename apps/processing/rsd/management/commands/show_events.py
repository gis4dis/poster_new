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

# ./dcmanage.sh show_events --geometry 'POINT(5 23)' --categories ['Práce na silnici','Nehoda'] --time_range "DateTimeTZRange(datetime.datetime(2017, 11, 24, 8, 55, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), datetime.datetime(2017, 11, 24, 9, 55, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), '[)')" --buffer 10.5


    def add_arguments(self, parser):
        parser.add_argument('--geometry', nargs='?', type=str,
                            default=None)
        parser.add_argument('--categories', nargs='?', type=list,
                            default=None)
        parser.add_argument('--time_range', nargs='?', type=str,
                            default=None)
        parser.add_argument('--buffer', nargs='?', type=float,
                            default=None)

    def handle(self, *args, **options):
        geom = options['geometry']
        categories_param = options['categories']
        time_range_param = options['time_range']
        buffer = options['buffer']
        if geom is None:
            raise Exception("No geometry defined!")
        else:
            geom = GEOSGeometry(geom, srid=3857)
        
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

        if time_range_param is None:
            raise Exception("No time range defined!")
        else:
            time_range = time_range_param
            start_range = time_range.lower
            end_range = time_range.upper
        print(time_range)
        print(type(time_range))


        if buffer is None:
            raise Exception("No buffer defined!")
        else:
            buffer = buffer
        print(buffer)

        i = 0
        result = []
        for event in EventObservation.objects.iterator():
            i += 1
            if(i == 10):
                break
            is_geometry = False
            is_category = False
            is_time = False
            
            for category in categories:
                if(category == event.category.name):
                    is_category = True
            
            start_time = event.phenomenon_time_range.lower
            end_time = event.phenomenon_time_range.upper
            print(type(start_time))            
            print(type(start_range))
            print(start_range)
            is_time = time_in_range(start_time, end_time, start_range, end_range)
            print(is_time)


def time_in_range(start, end, day_start, day_end):
    """Return true if event time range overlaps day range"""
    if (start <= day_start and end >= day_end):
        return True
    elif (start >= day_start and start <= day_end):
        return True
    elif (end >= day_start and end <= day_end):
        return True
    return False

            