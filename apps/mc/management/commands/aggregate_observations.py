import logging
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)
from apps.mc.tasks import compute_aggregated_values


#TODO unit tests
#TODO overit agregace ve srovnani s puvodnim agg metodou v importu ala
class Command(BaseCommand):
    help = 'Calculation of aggregated values'

    def add_arguments(self, parser):
        parser.add_argument('aggregate_updated_since', nargs='?', default=None)

    def handle(self, *args, **options):
        compute_aggregated_values.apply_async(kwargs={'aggregate_updated_since_datetime':(options['aggregate_updated_since'])})
