from django.contrib.gis.utils import LayerMapping
from apps.processing.rsd.models import AdminUnit
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import os


class Command(BaseCommand):
    help = 'Create admin units from shapefile. ' \
            'Path to file e.g.: \'shapefiles/rsd/momc_4326.shp\''
    # put SHP files into S3 storage
    # for devel it's var/s3storage/media/shapefiles/rsd/...

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        arg = options['path']
        if arg is None:
            raise Exception("No path to file defined!")
        else:
            path = arg
            import_towns(path)

def import_towns(path):
    print('Importing administrative units')
    basedir, filename = os.path.split(path)
    basedir += os.sep
    basename, _ = os.path.splitext(path)

    local_dir = os.path.join('/tmp/gis4dis', basedir)
    os.makedirs(local_dir, mode=0o770, exist_ok=True)

    for f in default_storage.listdir(basedir):
        f_basename, _ = os.path.splitext(f.object_name)
        if f_basename != basename:
            continue

        with default_storage.open(f.object_name, mode='rb') as f2, open(os.path.join('/tmp/gis4dis', f.object_name), mode='wb') as g:
            g.write(f2.read())

    mapping = {
        'id_by_provider' : 'Kod_char',
        'name' : 'Nazev',
        'geometry' : 'POLYGON', # For geometry fields use OGC name.
        'level': 'level',
            }
    lm = LayerMapping(AdminUnit, os.path.join('/tmp/gis4dis', path), mapping)
    lm.save(verbose=False)