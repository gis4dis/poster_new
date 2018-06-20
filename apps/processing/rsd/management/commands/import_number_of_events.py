from django.db import models
from apps.processing.rsd.models import EventExtent, AdminUnit, EventObservation, CategoryCustomGroup, NumberOfEventsObservation
from apps.processing.rsd.management.commands.import_categories import parse_date
from apps.common.models import Property, Process
from apps.common.util.util import get_or_create_props
from django.core.management.base import BaseCommand
from psycopg2.extras import DateTimeTZRange
from apps.utils.time import UTC_P0100
from datetime import datetime, date, timedelta
from dateutil.parser import parse

class Command(BaseCommand):
    help = 'Imports number of events of all category custom group ' \
    'that emerged in phenomenon time rage within all AdminUnits. ' \
    'If no arguments - takes data from yesterday ' \
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
                    admin_geom = admin_unit.geometry
                    
                    number_events = NumberOfEventsObservation.objects.update_or_create(
                                    phenomenon_time_range= dt_range,
                                    observed_property=observed_property,
                                    feature_of_interest=admin_unit,
                                    procedure=procedure,
                                    category_custom_group=category,
                                )[0]
                    
                    events = EventObservation.objects.filter(
                        phenomenon_time_range__startswith__range=(time_from, time_to),
                        point_geometry__intersects=admin_geom,
                        category__custom_group=category
                        )
                            
                    number_events.result = len(events)
                    number_events.save()

            print('Time {} {}'.format(time_from, time_to))
            time_from = time_from + timedelta(hours=1)
            time_to = time_to + timedelta(hours=1)
            dt_range = DateTimeTZRange(time_from, time_to)   
