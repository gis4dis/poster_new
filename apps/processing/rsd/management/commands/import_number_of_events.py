from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation
from apps.processing.rsd.management.commands.import_categories import parse_date
from apps.common.models import Property, Process
from apps.common.util.util import get_or_create_props
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

        whole_extent = EventExtent.objects.get(name_id="brno_brno_venkov_d1")
        whole_extent_units = whole_extent.admin_units.all()

        get_or_create_props()
        observed_property = Property.objects.get(name_id="number_of_emerged_events")
        procedure = Process.objects.get(name_id="observation")
        # for event in ProviderLog.objects.filter(received_time__range=(day_from, day_to)).iterator():
        
        for admin_unit in whole_extent_units:

            
