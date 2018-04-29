from django.core.management.base import BaseCommand
from apps.processing.ala.util.util import get_or_create_processes, get_or_create_props
from apps.processing.ozp.util.util import get_or_create_ozp_stations
from apps.processing.ozp.models import Observation
from dateutil.parser import parse
from datetime import datetime, date, timedelta, timezone
from apps.utils.time import UTC_P0100
from psycopg2.extras import DateTimeTZRange
import os
import csv

class Command(BaseCommand):
    help = 'Import data from OZP stations.'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str, default=None)

    def handle(self, *args, **options):
        stations = get_or_create_ozp_stations()
        properties = get_or_create_props()
        processes = get_or_create_processes()
        arg = options['path']
        # Observation.objects.all().delete()
        if arg is None:
            raise Exception("No path to folder defined!")
        else:
            for process in processes:
                if(process.name_id == 'measure'):
                    ozp_process = process
                    break
            path = arg
            file_count = 0
            files = len(os.listdir(path))
            for filename in os.listdir(path):
                file_count += 1
                file_stations = []
                file_property = None
                for prop in properties:
                    if(prop.name_id == filename[0:-4].lower()):
                        file_property = prop
                        break
                
                with open(os.path.join(path, filename), encoding='Windows-1250') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    i = 0
                    for row in csv_reader:
                        if(i == 0):
                            for indx, data in enumerate(row):
                                for station in stations:
                                    if(station.id_by_provider == data):
                                        file_stations.append(station)
                        else:
                            next_day = False
                            date = row[0]
                            start_hour = str((int(row[1]) - 1)) + ':00'
                            end_hour = str(int(row[1])) + ':00'
                            if(end_hour == '24:00'):
                                end_hour = '23:59'
                                next_day = True
                            time_start = parse_time(date + ' ' + start_hour)
                            time_end = parse_time(date + ' ' + end_hour)
                            if(next_day):
                                time_end = time_end + timedelta(0,60)
                            time_range = DateTimeTZRange(time_start, time_end)
                            
                            for indx, data in enumerate(row):
                                if(indx > 1):
                                    station = file_stations[(indx - 2)]
                                    if(data.find(',') > -1):
                                        result = float(data.replace(',','.'))
                                    elif(data == ''):
                                        continue
                                    else:
                                        result = float(data)
                                    print('Name: {} | File: {}/{} | Row: {}'.format(file_property, file_count, files, i))
                                    observation = Observation(
                                        phenomenon_time_range= time_range,
                                        observed_property=file_property,
                                        feature_of_interest=station,
                                        procedure=ozp_process,
                                        result=result)
                                    observation.save()

                        i += 1

            return

def parse_time(string):
    time = parse(string)
    time = time.replace(tzinfo=timezone.utc)
    time = time.astimezone(UTC_P0100)
    return time