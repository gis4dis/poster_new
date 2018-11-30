import csv
import io
import os
import time
from datetime import timedelta, timezone

from dateutil.parser import parse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from psycopg2.extras import DateTimeTZRange

from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.ozp.models import Observation
from apps.processing.ozp.util.util import get_or_create_ozp_stations
from apps.utils.time import UTC_P0100


class Command(BaseCommand):
    help = 'Import data from OZP stations. Path to folder with csv files.'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str, default='apps.processing.ozp/2017/')

    def handle(self, *args, **options):
        start = time.time()
        stations = get_or_create_ozp_stations()
        properties = get_or_create_props()
        processes = get_or_create_processes()
        arg = options['path']
        # Observation.objects.all().delete()

        if arg is None:
            raise Exception("No path to folder defined!")
        else:
            ozp_process = None
            for process in processes:
                if process.name_id == 'measure':
                    ozp_process = process
                    break

            path = os.path.join(settings.IMPORT_ROOT, arg, '')
            file_count = 0
            listed = default_storage.listdir(path)
            # files = len(listed)
            for filename in listed:
                char_ix = filename.object_name.rfind('/') + 1
                file_csv_name = filename.object_name[char_ix:-4]
                file_count += 1
                file_stations = []
                file_property = None
                for prop in properties:
                    if prop.name_id == file_csv_name.lower():
                        file_property = prop
                        break
                if file_property is None:
                    print('Error: no property exists to match the file: {}'.format(file_csv_name))
                    continue
                print('Processing | Name: {} | File: {}'.format(file_property, file_count))
                path = filename.object_name
                csv_file = default_storage.open(name=path, mode='r')
                foo = csv_file.data.decode('Windows-1250')
                reader = csv.reader(io.StringIO(foo), delimiter=';')
                rows = list(reader)
                i = 0
                for row in rows:
                    if i == 0:
                        for indx, data in enumerate(row):
                            for station in stations:
                                if station.id_by_provider == data:
                                    file_stations.append(station)
                    else:
                        next_day = False
                        date = row[0]
                        start_hour = str((int(row[1]) - 1)) + ':00'
                        end_hour = str(int(row[1])) + ':00'
                        if end_hour == '24:00':
                            end_hour = '23:59'
                            next_day = True
                        time_start = parse_time(date + ' ' + start_hour)
                        time_end = parse_time(date + ' ' + end_hour)
                        if next_day:
                            time_end = time_end + timedelta(0, 60)
                        time_range = DateTimeTZRange(time_start, time_end)

                        for indx, data in enumerate(row):
                            if indx > 1:
                                station = file_stations[(indx - 2)]
                                if data.find(',') > -1:
                                    result = float(data.replace(',', '.'))
                                elif data == '':
                                    result = None
                                    observation = Observation(
                                        phenomenon_time_range=time_range,
                                        observed_property=file_property,
                                        feature_of_interest=station,
                                        procedure=ozp_process,
                                        result=result,
                                        result_null_reason='empty string in CSV')
                                    observation.save()
                                    continue
                                else:
                                    result = float(data)
                                observation = Observation(
                                    phenomenon_time_range=time_range,
                                    observed_property=file_property,
                                    feature_of_interest=station,
                                    procedure=ozp_process,
                                    result=result)
                                observation.save()

                    i += 1
            end = round(((time.time() - start) / 60))
            print('Minutes: {}'.format(end))
            return


def parse_time(string):
    time_obj = parse(string)
    time_obj = time_obj.replace(tzinfo=timezone.utc)
    time_obj = time_obj.astimezone(UTC_P0100)
    return time_obj
