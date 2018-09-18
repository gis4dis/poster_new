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

    days_frequency = timeseries.frequency.days
    hours_frequency = timeseries.frequency.hours
    minutes_frequency = timeseries.frequency.minutes
    seconds_frequency = timeseries.frequency.seconds

    total_seconds_frequency = days_frequency * intervals["days"]
    total_seconds_frequency += hours_frequency * intervals["hours"]
    total_seconds_frequency += minutes_frequency * intervals["minutes"]
    total_seconds_frequency += seconds_frequency * intervals["seconds"]

    diff_until_from = (from_datetime - first_start.lower).total_seconds()
    diff_until_to = (to_datetime - first_start.lower).total_seconds()

    intervals_before_start = diff_until_from / total_seconds_frequency
    intervals_until_end = diff_until_to / total_seconds_frequency

    first_interval_counter = int(intervals_before_start)
    last_interval_counter = int(intervals_until_end) + 1

    '''
    intervals_until_end_modulo = diff_until_to % total_seconds_frequency
    if intervals_until_end_modulo > 0:
        last_interval_counter += 1
    '''

    slots = []

    if (first_interval_counter < 0) and (last_interval_counter > 0):
        first_interval_counter = 0

    print('first_interval_counter: ', first_interval_counter )
    print('last_interval_counter: ', last_interval_counter)

    if (first_interval_counter >= 0) and (last_interval_counter > first_interval_counter):
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

        default_zero = datetime(2000, 1, 1, 0, 00, 00)
        default_zero = default_zero.replace(tzinfo=UTC_P0100)

        #1-hour slots every hour
        t_1_hour_slots_every_hour = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )

        '''
        generate_intervals(
            timeseries=t_1_hour_slots_every_hour,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 4, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        #2-hour slots every 2 hours
        t_2_hour_slots_every_2_hours = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=2),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=2)
        )
        '''
        generate_intervals(
            timeseries=t_2_hour_slots_every_2_hours,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 4, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        #24-hour slots every hour
        t_24_hour_slots_every_2_hours = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=12),
            range_to=relativedelta(hours=1)
        )

        '''
        generate_intervals(
            timeseries=t_24_hour_slots_every_2_hours,
            from_datetime=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 2, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        #1 - week slots every week starting on Monday
        t_1_week_slots_every_week_starting_monday = TimeSeries(
            zero=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(days=7)
        )

        t2_1_week_slots_every_week_starting_monday = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=2),
            range_to=relativedelta(days=9)
        )

        t3_1_week_slots_every_week_starting_monday = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=-5),
            range_to=relativedelta(days=2)
        )

        '''
        generate_intervals(
            timeseries=t_1_week_slots_every_week_starting_monday,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        generate_intervals(
            timeseries=t2_1_week_slots_every_week_starting_monday,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        generate_intervals(
            timeseries=t3_1_week_slots_every_week_starting_monday,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        #3 - hour slots every Wednesday from 8: 00 to 11: 00
        t_3_hour_slots_wednesday_from_8_to_11 = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=4, hours=8),
            range_to=relativedelta(days=4, hours=11)
        )
        '''
        generate_intervals(
            timeseries=t_3_hour_slots_wednesday_from_8_to_11,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        # 1-day slots every last day of week
        t_1_day_slots_last_day_of_week = TimeSeries(
            zero=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(weeks=1),
            range_from=relativedelta(days=-1),
            range_to=relativedelta(0)
        )

        '''
        generate_intervals(
            timeseries=t_1_day_slots_last_day_of_week,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        #TODO
        #1-day slots every last day of month
        t_1_day_slots_last_day_of_month = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(months=7),
            range_from=relativedelta(days=4, hours=8),
            range_to=relativedelta(days=4, hours=11)
        )

        #TODO - MESICE A ROKY
        #TODO - omezujici parametry
        #TODO - pokryt to testy



        t2 = TimeSeries(
            zero=datetime(2018, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=4),
            range_to=relativedelta(hours=3)
        )

        t3 = TimeSeries(
            zero=datetime(2018, 5, 5, 5, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(hours=2),
            range_from=relativedelta(hours=2),
            range_to=relativedelta(hours=2)
        )



        '''
        intervals = generate_intervals(
            timeseries=t2,
            from_datetime=datetime(2018, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2018, 1, 1, 5, 00, 00).replace(tzinfo=UTC_P0100),
        )
        '''

        '''
        intervals = generate_intervals(
            timeseries=t2,
            from_datetime=datetime(2018, 5, 5, 5, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2018, 5, 5, 10, 00, 00).replace(tzinfo=UTC_P0100)
        )
        '''


        self.assertEqual(intervals, False)
