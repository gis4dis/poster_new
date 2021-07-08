from datetime import datetime, timedelta

from dateutil.rrule import rrule, DAILY

from apps.processing.ala.util.util import count_observations
from apps.utils.time import UTC_P0100


def check_ala():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC_P0100)
    two_days_ago = today - timedelta(days=3)
    response_dict = {}
    daily_count = count_observations(two_days_ago)
    daily_agg_count = count_observations(two_days_ago, aggregated=True)
    response_dict["measured-today-3"] = daily_count
    response_dict["aggregated-today-3"] = daily_agg_count
    response_dict["date"] = two_days_ago
    return response_dict
