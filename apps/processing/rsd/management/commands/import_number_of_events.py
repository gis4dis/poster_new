from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, CategoryCustomGroup, NumberOfEventsObservation
from apps.processing.rsd.management.commands.import_categories import parse_date
from apps.common.models import Property, Process
from apps.common.util.util import get_or_create_props
from django.core.management.base import BaseCommand
from psycopg2.extras import DateTimeTZRange
import xml.etree.ElementTree as ET
from apps.utils.time import UTC_P0100
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from django.contrib.gis.geos import GEOSGeometry, Point

class Command(BaseCommand):
    help = 'Create extents from events. If no arguments - takes data from yesterday ' \
    './dcmanage.sh import_number_of_events --date_from=2018-01-01 --date_to=2018-01-02'

    def add_arguments(self, parser):
        parser.add_argument('--date_from', nargs='?', type=str,
                            default=None)
        parser.add_argument('--date_to', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        
        # NumberOfEventsObservation.objects.all().delete()

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
        
        custom_categories = CategoryCustomGroup.objects.all()

        get_or_create_props()
        observed_property = Property.objects.get(name_id="number_of_emerged_events")
        procedure = Process.objects.get(name_id="observation")
        
        time_from = day_from
        time_to = time_from + timedelta(hours=1)
        dt_range = DateTimeTZRange(time_from, time_to)

        while(time_to <= day_to):
            for category in custom_categories:
                for admin_unit in whole_extent_units:
                    admin_list = [admin_unit]
                    admin_geom = admin_unit.geometry
                    i = 0
                    
                    number_events = NumberOfEventsObservation(
                                    phenomenon_time_range= dt_range,
                                    observed_property=observed_property,
                                    feature_of_interest=admin_unit,
                                    procedure=procedure,
                                    category_custom_group=category,
                                    result=i,
                                )
                    number_events.save()
                    for event in EventObservation.objects.filter(
                        phenomenon_time_range__startswith__range=(time_from, time_to),
                        result__admin_units__in=admin_list,
                        category__custom_group=category
                        ).iterator():

                            if(event.point_geometry.intersects(admin_geom)):
                                number_events.result = number_events.result + 1
                                number_events.save()

            print('Time {} {}'.format(time_from, time_to))
            time_from = time_from + timedelta(hours=1)
            time_to = time_to + timedelta(hours=1)
            dt_range = DateTimeTZRange(time_from, time_to)          
        print('Done')
