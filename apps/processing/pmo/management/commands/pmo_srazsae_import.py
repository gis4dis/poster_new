from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from dateutil.parser import parse
from psycopg2.extras import DateTimeTZRange
from apps.utils.time import UTC_P0100
from apps.processing.pmo.util.util import parse_date_range
from datetime import datetime
import csv
from apps.common.models import Process, Property
from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.pmo.models import WeatherStation, WeatherObservation
import io
import re

class Command(BaseCommand):
    help = 'Imports all stations and all observations from files within the date range' \
        './dcmanage pmo_srazsae_import --date_range "24 11 2017"' \
        'docker-compose run --rm poster-web python manage.py pmo_srazsae_import --date_range "24 11 2017"'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str,
                            default='/import/apps.processing.pmo/')
        parser.add_argument('--date_range', nargs='?', type=parse_date_range,
                            default=[None, None])

    def handle(self, *args, **options):

        # WeatherObservation.objects.all().delete()

        path = options['path']
        day_from, day_to = options['date_range']
        if day_from is None or day_to is None:
            raise Exception("Wrong date range")

        get_or_create_processes()
        get_or_create_props()
        measure = Process.objects.get(name_id="measure")
        air_temperature = Property.objects.get(name_id="air_temperature")
        precipitation = Property.objects.get(name_id="precipitation")

        content = tuple(default_storage.listdir(path))
        for con in content:
            folder_name = get_name(con.object_name)
            print("Import from folder")
            print(folder_name)
            try:
                date_from_name = datetime.strptime(folder_name, "%Y%m%d")
                if(day_from <= date_from_name < day_to):
                    files = tuple(default_storage.listdir(con.object_name))
                    for f in files:
                        file_name = get_name(f.object_name)
                        if(file_name == "srazsae.dat"):
                            csv_file = default_storage.open(name=f.object_name, mode='r')
                            foo = csv_file.data.decode('utf-8')
                            reader = csv.reader(io.StringIO(foo), delimiter=" ")

                            rows = list(reader)
                            
                            for rid_x, row in enumerate(rows, 1):
                                weather_station = WeatherStation.objects.get_or_create(
                                    id_by_provider=row[0],
                                    name=row[0]
                                    )[0]

                                parsed = parse(row[2] + " " + row[3])
                                time = parsed.astimezone(UTC_P0100) 
                                dt_range = DateTimeTZRange(time, time, bounds="[]")
                                observed_property = air_temperature if row[1] == '32' else precipitation
                    
                                WeatherObservation.objects.get_or_create(
                                    phenomenon_time_range=dt_range,
                                    observed_property=observed_property,
                                    feature_of_interest=weather_station,
                                    procedure=measure,
                                    result=row[5]
                                )
                else:
                    continue
            except Exception as e: 
                print(e)
        print("Done!")


def get_name(path):
        if(path[-1:] == "/"):
            folder_name = path[:-1]
        else:
            folder_name = path
        i = folder_name.rfind("/") + 1
        return folder_name[i:]