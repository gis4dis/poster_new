import csv
import io
import os
from datetime import timedelta, timezone

from dateutil.parser import parse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from psycopg2.extras import DateTimeTZRange

from apps.common.models import Property, Process
from apps.common.util.util import get_or_create_processes, get_or_create_props
from apps.processing.huaihe.models import Observation, SamplingFeature
from apps.processing.huaihe.util.util import get_or_create_huaihe_stations
from apps.utils.time import UTC_P0100


class Command(BaseCommand):
    help = 'Import data from Huaihe River stations. Path to folder with csv files.'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str, default='apps.processing.huaihe/2017/')

    def handle(self, *args, **options):
        get_or_create_huaihe_stations()
        get_or_create_processes()
        get_or_create_props()
        arg_path = options['path']
        # Observation.objects.all().delete()

        if arg_path is None:
            raise Exception("No path to folder defined!")

        process = Process.objects.get(name_id='measure')

        path = os.path.join(settings.IMPORT_ROOT, arg_path, '')
        file_count = 0
        listed = default_storage.listdir(path)
        # files = len(listed)
        for filename in listed:
            char_idx = filename.object_name.rfind('/') + 1
            file_csv_name = filename.object_name[char_idx:-4]
            file_count += 1
            file_property = Property.objects.get(name_id=file_csv_name.lower())

            if file_property is None:
                print('Error: no property exists to match the file: {}'.format(file_csv_name))
                continue

            print('Processing | Name: {} | File: {}'.format(file_property, file_count))
            path = filename.object_name
            csv_file = default_storage.open(name=path, mode='r')
            foo = csv_file.data.decode('UTF-8')
            reader = csv.reader(io.StringIO(foo), delimiter=',')
            rows = list(reader)
            rows.pop(0)
            for row in rows:
                station = SamplingFeature.objects.get(id_by_provider=row[0])
                time_start = parse_datetime(row[2])
                time_end = time_start + timedelta(1)
                time_range = DateTimeTZRange(time_start, time_end)

                result = float(row[3])
                observation = Observation(
                    phenomenon_time_range=time_range,
                    observed_property=file_property,
                    feature_of_interest=station,
                    procedure=process,
                    result=result)
                observation.save()

        return


def parse_datetime(datestr):
    dateparts = datestr.split(' ')
    assert dateparts[1] == '0:00'
    time_obj = parse(dateparts[0])
    time_obj = time_obj.replace(tzinfo=UTC_P0100)
    return time_obj
