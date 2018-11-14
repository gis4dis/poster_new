import logging
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

from apps.processing.pmo.util import util
from apps.processing.pmo.util.util import parse_date_range

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Imports all stations and all observations from srazsae.dat files within the date range' \
           './dcmanage.sh pmo_srazsae_import --date_range "24 11 2017"'

    def add_arguments(self, parser):
        parser.add_argument('date_range', nargs='?', type=parse_date_range,
                            default=[None, None])

    def handle(self, *args, **options):

        day_from, day_to = options['date_range']
        if day_from is None:
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = (today - timedelta(days=now.weekday()))
            last_week_start = week_start + timedelta(weeks=-1)

            day_from = last_week_start
            day_to = last_week_start + timedelta(1)

        day = day_from
        logger.info('Importing observations of PMO watercourse srazsae')

        while(day < day_to):
            logger.info('Importing from file - date: %s', day)
            util.load_srazsae(day)
            day += timedelta(1)