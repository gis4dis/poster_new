import logging
from django.core.management.base import BaseCommand
from apps.processing.pmo.util import util
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def parse_date_range(date_str):
    if len(date_str) == 4:
        day_from = parse(date_str).replace(day=1, month=1)
        day_to = day_from + relativedelta.relativedelta(years=1)
    elif len(date_str) == 7:
        day_from = parse(date_str).replace(day=1)
        day_to = day_from + relativedelta.relativedelta(months=1)
    else:
        day_from = parse(date_str)
        day_to = day_from + timedelta(1)
    return [day_from, day_to]


class Command(BaseCommand):
    help = 'Import data from ALA stations. Optionally you can pass date, ' \
           'otherwise it will fetch the day before yesterday data.'

    def add_arguments(self, parser):
        parser.add_argument('date_range', nargs='?', type=parse_date_range,
                            default=[None, None])

    def handle(self, *args, **options):

        day_from, day_to = options['date_range']
        if day_from is None:
            day_from = date.today() - timedelta(2)
            day_to = day_from + timedelta(1)

        day = day_from
        while(day < day_to):
            logger.info('Importing observations of PMO watercourse observation')
            util.load(day)
            day += timedelta(1)
