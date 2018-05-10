import logging
from django.core.management.base import BaseCommand
from apps.processing.pmo.util import util
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta, datetime

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

#import_watercourse_observation
#import_watercourse_observation 2018-04-09
class Command(BaseCommand):
    help = 'Import data from PMO watercourse stations. Optionally you can pass date, ' \
           'otherwise it will fetch last past monday.'

    def add_arguments(self, parser):
        parser.add_argument('date_range', nargs='?', type=parse_date_range,
                            default=[None, None])

    def handle(self, *args, **options):

        day_from, day_to = options['date_range']
        if day_from is None:
            now = datetime.now()
            #now = parse('2018-03-29')
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = (today - timedelta(days=now.weekday()))
            last_week_start = week_start + timedelta(weeks=-1)

            day_from = last_week_start
            day_to = last_week_start + timedelta(1)

        day = day_from
        logger.info('Importing observations of PMO watercourse observation')

        while(day < day_to):
            logger.info('Importing from file - date: %s', day)
            util.load(day)
            day += timedelta(1)
