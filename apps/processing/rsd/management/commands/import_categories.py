from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventCategory, EventObservation
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta
from apps.utils.time import UTC_P0100

class Command(BaseCommand):
    help = 'Create categories from events. If no arguments - takes data from yesterday ' \
    './dcmanage.sh import_categories --date_from=2018-01-01 --date_to=2018-01-01'

    def add_arguments(self, parser):
        parser.add_argument('--date_from', nargs='?', type=str,
                            default=None)
        parser.add_argument('--date_to', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        
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
        import_categories(day_from, day_to)

def import_categories(day_from, day_to):
    categories = []
    for cat in EventCategory.objects.all():
        category = cat.id_by_provider
        if not category in categories:
                categories.append(category)

    for event in ProviderLog.objects.filter(received_time__range=(day_from, day_to)).iterator():
        data = event.body
        tree = ET.fromstring(data)
        for msg in tree.iter('MSG'):
            for tag in msg.iter('EVI'):
                code = tag.attrib["eventcode"]
                category = ""
                for text in tag.iter('TXUCL'):
                    group = text.text
                    break
                for name in tag.iter('TXEVC'):
                    code_name = name.text
                    break
                        
                if not code in categories:
                    categories.append(code)
                    cat = EventCategory(group=group, name=code_name,id_by_provider=code)
                    cat.save()
    print('Categories in database: {}'.format(categories))
    print('=====================')
    print('Number of categories: {}'.format(len(categories)))

        
def parse_date(date_str, times):
    if len(date_str) == 4:
        day = parse(date_str).replace(day=1, month=1)
    elif len(date_str) == 7 or len(date_str) == 6:
        day = parse(date_str).replace(day=1)
    elif len(date_str) > 7 and len(date_str) < 11:
        day = parse(date_str)
    else:
        day = parse(date_str)
        return day
    if(times == 2):
        day = datetime.combine(day, datetime.min.time())
        day = day + timedelta(hours=24)
    return day