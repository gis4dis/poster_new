import logging
from django.core.management.base import BaseCommand
from celery import chain

logger = logging.getLogger(__name__)

from apps.mc.tasks import compute_aggregated_values, import_time_slots_from_config


class Command(BaseCommand):
    help = 'Calculation of aggregated values'

    def add_arguments(self, parser):
        parser.add_argument('aggregate_updated_since', nargs='?', default=None)

    def handle(self, *args, **options):
        #compute_aggregated_values()
        chain(import_time_slots_from_config.si() |
              compute_aggregated_values.si(aggregate_updated_since_datetime=options['aggregate_updated_since']))()