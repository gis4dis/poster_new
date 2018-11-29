from datetime import datetime, timedelta

from dateutil.rrule import rrule, DAILY

from apps.processing.ala.util.util import count_observations
from apps.processing.pmo.monitoring.checks import date_to_ymd
from apps.utils.time import UTC_P0100


def check_ala():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC_P0100)
    two_days_ago = today - timedelta(days=2)
    two_weeks_ago = today - timedelta(days=14)

    error_dict = {}

    # Populate for last 30 days
    for day in list(rrule(DAILY, dtstart=two_weeks_ago, until=two_days_ago)):
        daily_count = count_observations(day)
        # TODO: count is 4896?
        if daily_count != 5424:
            error_dict[date_to_ymd(day)] = daily_count

    return error_dict

