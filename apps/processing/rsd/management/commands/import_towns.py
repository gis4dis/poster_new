from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from apps.processing.rsd.models import AdminUnit
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create admin units from shapefile. ' \
            'Path to file e.g.: \'var/data/obce_4326.shp\''

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str,
                            default=None)

    def handle(self, *args, **options):
        arg = options['path']
        if arg is None:
            raise Exception("No path to file defined!")
        else:
            path = arg
        mapping = {
            'id_by_provider' : 'Kod_char',
            'name' : 'Nazev',
            'geometry' : 'POLYGON', # For geometry fields use OGC name.
            'level': 'level',
               }
        lm = LayerMapping(AdminUnit, path, mapping)
        lm.save(verbose=True)
        
