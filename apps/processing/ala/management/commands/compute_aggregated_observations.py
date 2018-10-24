import logging
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

#TODO tests
#TODO overit pro tu alu

from apps.mc.tasks import compute_aggregated_values

class Command(BaseCommand):
    help = 'Calculation of aggregated values'

    def add_arguments(self, parser):
        parser.add_argument('aggregate_updated_since', nargs='?', default=None)

    def handle(self, *args, **options):
        compute_aggregated_values.apply_async(kwargs={'aggregate_updated_since_datetime':(options['aggregate_updated_since'])})
