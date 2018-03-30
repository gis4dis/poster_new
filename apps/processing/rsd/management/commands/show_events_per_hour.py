from django.db import models
from apps.importing.models import ProviderLog
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta, tz
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from apps.utils.time import UTC_P0100

class Command(BaseCommand):
    help = 'Get RSD logger info. Optionally you can pass date as a string, ' \
           '(e.g.  python manage.py rsd --date_range "1 16 2018" otherwise it' \
            'will fetch the data from yesterday.'

    def add_arguments(self, parser):
        parser.add_argument('--date_range', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        arg = options['date_range']
        if arg is None:
            day_from = date.today() - timedelta(2)
            day_to = day_from + timedelta(1)
        else:
            day_from = parse_date_range(arg)[0]
            day_to = parse_date_range(arg)[1]

        day = day_from
        tz = UTC_P0100
    
        day_log = ProviderLog.objects

        while(day < day_to):
            events = 0
            day_start = day
            day_start = datetime(day.year, day.month, day.day)
            day_end = day + timedelta(hours=24)
            day_end = datetime(day_end.year, day_end.month, day_end.day)
            day_start = day_start.replace(tzinfo=tz)
            day_end = day_end.replace(tzinfo=tz)
            towns = []
            categories = []
            hours = []
            # total number of events for town & category & hour trio - same indexes in lists
            total = []

            for event in day_log.iterator():
                # encoding troubles...
                data = event.body
                tree = ET.fromstring(data)

                for tag in tree.iter('TSTA'):
                    start_time = parse(tag.text)
                for tag in tree.iter('TSTO'):
                    end_time = parse(tag.text)
                    
                start_time = start_time.astimezone(UTC_P0100) 
                end_time = end_time.astimezone(UTC_P0100)
                    
                if(time_in_range(start_time, end_time, day_start, day_end)):
                    for tag in tree.iter('DEST'):
                        road = tag.find('ROAD')
                        is_d1 = False
                        if road is not None and 'RoadNumber' in road.attrib:
                            is_d1 = True if road.attrib['RoadNumber'] == 'D1' else False

                        town_ship = tag.attrib['TownShip']
                        if((town_ship == 'Brno-venkov' or town_ship == 'Brno-město') or (is_d1)):
                            hours_range = get_hours(start_time, end_time, day_start, day_end)      
                            for cat in tree.iter('TXUCL'):
                                category = cat.text
                                break
                            events += 1
                            # check if category & town & hour trio already exists
                            hour_indexes = []
                            category_town_idx = []
                            event_hours = []
                            town = tag.attrib['TownName']  

                            category_indexes = [i for i, x in enumerate(
                                categories) if x == category]
                            town_indexes = [
                                i for i, x in enumerate(towns) if x == town]
                            intersect = set(category_indexes).intersection(
                                town_indexes)

                            for hour in range(hours_range[0],hours_range[1] + 1):
                                hour_indexes.extend(i for i, x in enumerate(hours) if x == hour)
                                event_hours.append(hour)

                            for e in intersect:
                                category_town_idx.append(e)

                            trio_intersect = set(category_town_idx).intersection(
                                hour_indexes)
                            trio_intersect = list(trio_intersect)
                            if(len(trio_intersect) > 0):
                                for e in trio_intersect:
                                    shared_index = e
                                    total[shared_index] = total[shared_index] + 1
                                    event_hours.remove(hours[shared_index])
                                # if event lasts longer
                                if(len(event_hours) != 0):
                                    for hour in event_hours:
                                        towns.append(town)
                                        categories.append(category)
                                        total.append(1)
                                        hours.append(hour)
                            else:
                                for hour in range(hours_range[0], hours_range[1] + 1):
                                    towns.append(town)
                                    categories.append(category)
                                    total.append(1)
                                    hours.append(hour)

            print('Categories: {}'.format(categories))
            print('---')
            print('Towns: {}'.format(towns))
            print('---')
            print('Hours: {}'.format(hours))
            print('---')
            print('Number of events for town & category & hour (same indexes in lists): {}'.format(total))
            print('---')
            print('Total number of events: {}'.format(events))
            print('Total number of events by hour: {}'.format(sum(total)))
            print('Day: {}'.format(day))
            print('=========================\n=========================')
            day += timedelta(1)      

def time_in_range(start, end, day_start, day_end):
    """Return true if event time range overlaps day range"""
    if (start <= day_start and end >= day_end):
        return True
    elif (start >= day_start and start <= day_end):
        return True
    elif (end >= day_start and end <= day_end):
        return True
    return False

def get_hours(start, end, day_start, day_end):
    """Return hours range of an event for the day"""
    if (start <= day_start and end >= day_end):
        return [0, 24]
    elif (start >= day_start and start <= day_end):
        if(end >= day_end):
            return [start.hour, 24]
        else:
            return [start.hour, end.hour]
    elif (end >= day_start and end <= day_end):
        return [0, end.hour]
    return False
        

def parse_date_range(date_str):
    if len(date_str) == 4:
        day_from = parse(date_str).replace(day=1, month=1)
        day_to = day_from + relativedelta.relativedelta(years=1)
    elif len(date_str) == 7 or len(date_str) == 6:
        day_from = parse(date_str).replace(day=1)
        day_to = day_from + relativedelta.relativedelta(months=1)
    else:
        day_from = parse(date_str)
        day_to = day_from + timedelta(1)
    return [day_from, day_to]