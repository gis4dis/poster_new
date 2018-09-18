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
    "years": 29030400,  # 60 * 60 * 24 * 7 * 4 * 12
    "months": 2419200,  # 60 * 60 * 24 * 7 * 4
    "weeks": 604800,    # 60 * 60 * 24 * 7
    "days": 86400,      # 60 * 60 * 24
    "hours": 3600,      # 60 * 60
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
    first_start = DateTimeTZRange(
        lower=timeseries.zero + 0 * timeseries.frequency + timeseries.range_from,
        upper=timeseries.zero + 0 * timeseries.frequency + timeseries.range_to)

    years_frequency = timeseries.frequency.years
    months_frequency = timeseries.frequency.months
    days_frequency = timeseries.frequency.days
    hours_frequency = timeseries.frequency.hours
    minutes_frequency = timeseries.frequency.minutes
    seconds_frequency = timeseries.frequency.seconds

    if years_frequency or months_frequency:
        total_seconds_frequency = years_frequency * intervals["years"]
        total_seconds_frequency += months_frequency * intervals["months"]
    else:
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

    slots = []

    if (first_interval_counter < 0) and (last_interval_counter > 0):
        first_interval_counter = 0

    '''
    range.lower < INPUT.to
    range.upper > INPUT.from
    range.lower >= INPUT.range_from_limit
    range.upper < INPUT.range_to_limit
    '''

    if (first_interval_counter >= 0) and (last_interval_counter > first_interval_counter):
        for N in range(first_interval_counter, last_interval_counter):
            slot = DateTimeTZRange(
                lower=timeseries.zero + N * timeseries.frequency + timeseries.range_from,
                upper=timeseries.zero + N * timeseries.frequency + timeseries.range_to)
            # Check if slot is after from_datetime
            print('-------------check conditions-------------')
            if from_datetime <= slot.upper:
                condition = True
                if range_from_limit and slot.lower < range_from_limit:
                    condition = False

                if range_to_limit and slot.upper >= range_to_limit:
                    condition = False

                if condition:
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


default_zero = datetime(2000, 1, 1, 0, 00, 00)
default_zero = default_zero.replace(tzinfo=UTC_P0100)


# TODO - omezujici parametry
# TODO - udelat omezeni na urovni modelu
# TODO pokud je frequency libovolna kombinace mesicu a let, tak zero musi mit den v mesici <= 28

class TimeSeriesTestCase(TestCase):
    def setUp(self):
        create_test_timeseries()

    def test_hour_slots_every_hour(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 2, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 3, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_2_hour_slots_every_hour(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=2)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 5, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 6, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 5, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 7, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 6, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 8, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_week_slots(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(days=7)
        )

        t2 = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=2),
            range_to=relativedelta(days=9)
        )

        t3 = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=-5),
            range_to=relativedelta(days=2)
        )

        i1 = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        i2 = generate_intervals(
            timeseries=t2,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        i3 = generate_intervals(
            timeseries=t3,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 10, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 10, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 17, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 17, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 24, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 24, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 31, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 31, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 2, 7, 0, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, i1)
        self.assertEqual(i1, i2)
        self.assertEqual(i1, i3)
        self.assertEqual(i2, i3)

    def test_3_hour_slots_wednesday_from_8_to_11(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=4, hours=8),
            range_to=relativedelta(days=4, hours=11)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 5, 8, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 5, 11, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 12, 8, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 12, 11, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 19, 8, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 19, 11, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 26, 8, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 26, 11, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_day_slot_last_day_of_week(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(weeks=1),
            range_from=relativedelta(days=-1),
            range_to=relativedelta(0)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 15, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 2, 12, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 16, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 17, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 23, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 24, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 30, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 31, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 2, 6, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 2, 7, 0, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_last_day_of_month(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(months=1),
            range_from=relativedelta(days=-1),
            range_to=relativedelta(0)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 2, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 5, 31, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 2, 29, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 3, 1, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 3, 31, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 4, 1, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 4, 30, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 5, 1, 0, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 5, 31, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 6, 1, 0, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_interval_from_first_day_of_year(self):
        t = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(years=1),
            range_from=relativedelta(0),
            range_to=relativedelta(days=3, hours=3)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2002, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 1, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 4, 3, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2001, 1, 1, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2001, 1, 4, 3, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2002, 1, 1, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2002, 1, 4, 3, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_from_limit(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 2, 00, 00).replace(tzinfo=UTC_P0100),
            range_from_limit=datetime(2000, 1, 3, 1, 00, 00).replace(tzinfo=UTC_P0100),
            #range_to_limit
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 3, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_to_limit(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 2, 00, 00).replace(tzinfo=UTC_P0100),
            range_to_limit=datetime(2000, 1, 3, 3, 00, 00).replace(tzinfo=UTC_P0100)
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 0, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100)
            ),
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

    def test_limits(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 2, 00, 00).replace(tzinfo=UTC_P0100),
            range_from_limit=datetime(2000, 1, 3, 1, 00, 00).replace(tzinfo=UTC_P0100),
            range_to_limit=datetime(2000, 1, 3, 3, 00, 00).replace(tzinfo=UTC_P0100)
        )

        expected_slots = [
            DateTimeTZRange(
                lower=datetime(2000, 1, 3, 1, 0).replace(tzinfo=UTC_P0100),
                upper=datetime(2000, 1, 3, 2, 0).replace(tzinfo=UTC_P0100)
            )
        ]

        self.assertEqual(expected_slots, result_slots)

