from datetime import timedelta, datetime
from psycopg2._range import DateTimeTZRange
from apps.importing.models import ProviderLog
from apps.utils.time import UTC_P0100


def check_new_observations(hours):
    now = datetime.now().replace(tzinfo=UTC_P0100)
    response_dict = {}
    response_dict["check_datetime"] = now
    response_dict["hours"] = hours
    response_dict["provider_logs_count"] = count_observations(now, hours)
    return response_dict


def count_observations(day, hours):
    time_to = day
    time_from = day + timedelta(hours=hours)
    time_range_boundary = '[]' if time_from == time_to else '[)'
    pt_range = DateTimeTZRange(time_from, time_to, time_range_boundary)

    return ProviderLog.objects.filter(
        received_time__contained_by=pt_range
    ).count()
