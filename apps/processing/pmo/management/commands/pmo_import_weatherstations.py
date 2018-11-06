import logging
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import csv
from apps.processing.pmo.models import WeatherStation
from django.contrib.gis.geos import GEOSGeometry, Point
import io
import re

logger = logging.getLogger(__name__)


def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    degree = int(float(parts[0]))
    minute = int(float(parts[1]))
    second = int(float(parts[2]))
    ms = 0

    if parts[3]:
        ms = int(float(parts[3]))

    return degree, minute, second, ms


class Command(BaseCommand):
    help = 'Import stations '

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str,
                            default='/import/apps.processing.pmo/stanice_meteo.csv')


    def handle(self, *args, **options):
        path = options['path']

        if default_storage.exists(path):
            csv_file = default_storage.open(name=path, mode='r')
            foo = csv_file.data.decode('utf-8')
            reader = csv.reader(io.StringIO(foo))

            headers = next(reader)
            rows = list(reader)

            for rid_x, row in enumerate(rows, 1):
                id_by_prov = row[0]
                name = row[1]
                basin = row[2]

                (degree, minute, second, ms) = parse_dms(row[3])
                lat = (int(degree) + float(minute) / 60 + float(second) / 3600 + float(ms) / 36000)

                (degree, minute, second, ms) = parse_dms(row[4])
                lon = (int(degree) + float(minute) / 60 + float(second) / 3600 + float(ms) / 36000)

                geom = Point(lon, lat)

                if geom is None:
                    raise Exception("No geometry defined!")
                else:
                    geom = GEOSGeometry(geom, srid=4326)
                    geom = geom.transform(3857, clone=True)

                    defaults = {
                        'id_by_provider': id_by_prov,
                        'name': name,
                        'geometry': geom,
                        'basin': basin
                    }

                    WeatherStation.objects.update_or_create(
                        id_by_provider=id_by_prov,
                        defaults=defaults
                    )
        else:
            logger.warning("Error specified path: %s not found", path)

