from django.test import TestCase
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from apps.common.models import TimeSeries
from datetime import datetime
from apps.utils.time import UTC_P0100
from psycopg2.extras import DateTimeTZRange
from apps.common.util.util import generate_intervals

default_zero = datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100)


class TimeSeriesTestCase(TestCase):
    def test_hour_slots_every_hour(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=relativedelta(hours=1),
            range_from=relativedelta(hours=0),
            range_to=relativedelta(hours=1)
        )
        t.clean()

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
        t.clean()

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
        t.clean()

        t2 = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=2),
            range_to=relativedelta(days=9)
        )
        t2.clean()

        t3 = TimeSeries(
            zero=datetime(2000, 1, 1, 0, 00, 00).replace(tzinfo=UTC_P0100),
            frequency=relativedelta(days=7),
            range_from=relativedelta(days=-5),
            range_to=relativedelta(days=2)
        )
        t3.clean()

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
        t.clean()

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
        t.clean()

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
        t.clean()

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
        t.clean()

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
        t.clean()

        result_slots = generate_intervals(
            timeseries=t,
            from_datetime=datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100),
            to_datetime=datetime(2000, 1, 3, 2, 00, 00).replace(tzinfo=UTC_P0100),
            range_from_limit=datetime(2000, 1, 3, 1, 00, 00).replace(tzinfo=UTC_P0100)
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
        t.clean()

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
        t.clean()

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

    #TODO consult - valid values in t?
    def test_null_range(self):
        t = TimeSeries(
            zero=default_zero,
            frequency=None,
            range_from=None,
            range_to=None
        )
        t.clean()

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
