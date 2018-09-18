from django.test import TestCase
from dateutil import relativedelta
from relativedeltafield import RelativeDeltaField
from dateutil.relativedelta import relativedelta
from apps.common.models import TimeSeries
from datetime import datetime
from apps.utils.time import UTC_P0100
from psycopg2.extras import DateTimeTZRange

zero = datetime(2018, 5, 5, 5, 00, 00)
zero = zero.replace(tzinfo=UTC_P0100)

intervals = {
    "weeks": 604800,  # 60 * 60 * 24 * 7
    "days": 86400,    # 60 * 60 * 24
    "hours": 3600,    # 60 * 60
    "minutes": 60,
    "seconds": 1,
}

def generate_intervals(
    timeseries,         #: TimeSeries
    from_datetime,               #: datetime with timezone
    to_datetime,                 #: datetime with timezone
    range_from_limit=None,   #: datetime with timezone, default=datetime.min UTC+01:00
    range_to_limit=None     #: datetime with timezone, default=datetime.max UTC+01:00
):
    print('from_datetime: ', from_datetime)
    print('to_datetime: ', to_datetime)
    print('timeseries.zero: ', timeseries.zero)
    print('frequency: ', timeseries.frequency)

    first_start = DateTimeTZRange(
        lower=timeseries.zero + 0 * timeseries.frequency + timeseries.range_from,
        upper=timeseries.zero + 0 * timeseries.frequency + timeseries.range_to)

    print('FIRST START: ', first_start)

    years_from = timeseries.range_from.years
    months_from = timeseries.range_from.months
    days_from =  timeseries.range_from.days
    hours_from = timeseries.range_from.hours
    minutes_from = timeseries.range_from.minutes
    seconds_from = timeseries.range_from.seconds

    '''
    print('years_from: ', years_from)
    print('months_from: ', months_from)
    print('days_from: ', days_from)
    print('hours_from: ', hours_from)
    print('minutes_from: ', minutes_from)
    print('seconds_from: ', seconds_from)
    '''

    days_frequency = timeseries.frequency.days
    hours_frequency = timeseries.frequency.hours
    minutes_frequency = timeseries.frequency.minutes
    seconds_frequency = timeseries.frequency.seconds

    total_seconds_frequency = days_frequency * intervals["days"]
    total_seconds_frequency += hours_frequency * intervals["hours"]
    total_seconds_frequency += minutes_frequency * intervals["minutes"]
    total_seconds_frequency += seconds_frequency * intervals["seconds"]

    print('TOTAL_SECONDS: ', total_seconds_frequency)

    diff_until_from = (from_datetime - first_start.lower).total_seconds()
    diff_until_to = (to_datetime - first_start.lower).total_seconds()

    intervals_before_start = diff_until_from / total_seconds_frequency
    intervals_until_end = diff_until_to / total_seconds_frequency
    intervals_until_end_modulo = diff_until_to % total_seconds_frequency

    print('intervals_until_end_modulo: ', intervals_until_end_modulo)
    print('intervals_before_start: ', intervals_before_start )
    print('intervals_until_end: ', intervals_until_end)

    first_interval_counter = int(intervals_before_start)
    last_interval_counter = int(intervals_until_end) + 1
    if intervals_until_end_modulo > 0:
        last_interval_counter += 1

    slots = []
    for N in range(first_interval_counter, last_interval_counter):
        slot = DateTimeTZRange(
            lower=timeseries.zero + N * timeseries.frequency + timeseries.range_from,
            upper=timeseries.zero + N * timeseries.frequency + timeseries.range_to)
        print('--------------------------------------------')
        print(slot)
        slots.append(slot)

    return slots


def create_test_timeseries():
    TimeSeries(
        zero=zero,
        frequency=relativedelta(hours=2),
        range_from=relativedelta(hours=0),
        range_to=relativedelta(hours=2)
    )


class TimeSeriesTestCase(TestCase):
    def setUp(self):
        create_test_timeseries()

    def test_exists_delta(self):
        t = TimeSeries(
            zero=zero,
            frequency=relativedelta(hours=2),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=2)
        )

        zero_2 = datetime(2018, 1, 1, 0, 00, 00)
        zero_2 = zero_2.replace(tzinfo=UTC_P0100)

        zero_2_add_5 = datetime(2018, 5, 5, 5, 00, 00)
        zero_2_add_5 = zero_2_add_5.replace(tzinfo=UTC_P0100)

        zero_2_add_10 = datetime(2018, 5, 5, 10, 00, 00)
        zero_2_add_10 = zero_2_add_10.replace(tzinfo=UTC_P0100)

        t2 = TimeSeries(
            zero=zero_2,
            frequency=relativedelta(hours=2),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=2)
        )
        '''
        i = generate_intervals(
            timeseries=t2,
            from_datetime=zero_2,
            to_datetime=zero_2_add_5
        )
        '''

        intervals = generate_intervals(
            timeseries=t2,
            from_datetime=zero_2_add_5,
            to_datetime=zero_2_add_10
        )

        self.assertEqual(intervals, False)
