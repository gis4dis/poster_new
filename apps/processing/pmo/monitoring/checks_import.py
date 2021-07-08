from datetime import datetime, timedelta
from apps.processing.ala.util.util import count_observations
from apps.utils.time import UTC_P0100
from apps.common.models import Process
from apps.processing.pmo.models import WatercourseObservation, WeatherObservation
from psycopg2.extras import DateTimeTZRange


def check_pmo():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC_P0100)
    two_weeks_ago = today - timedelta(days=14)
    response_dict = {}

    daily_weather_count = count_observations(two_weeks_ago, WeatherObservation)
    daily_weather_agg_count = count_observations(two_weeks_ago, WeatherObservation, aggregated=True)

    daily_water_count = count_observations(two_weeks_ago, WatercourseObservation)
    daily_water_agg_count = count_observations(two_weeks_ago, WatercourseObservation, aggregated=True)

    response_dict["WeatherObservation-measured-today-14"] = daily_weather_count
    response_dict["WeatherObservation-aggregated-today-14"] = daily_weather_agg_count

    response_dict["WatercourseObservation-measured-today-14"] = daily_water_count
    response_dict["WatercourseObservation-aggregated-today-14"] = daily_water_agg_count

    response_dict["date"] = two_weeks_ago

    return response_dict


def count_observations(day, model, aggregated = False):
    time_from = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC_P0100)
    time_to = day + timedelta(days=1)
    time_range_boundary = '[]' if time_from == time_to else '[)'
    pt_range = DateTimeTZRange(time_from, time_to, time_range_boundary)

    measure_process_id = ['measure']
    aggregated_process_id = ["avg_hour", "avg_day", "apps.common.aggregate.arithmetic_mean", "apps.common.aggregate.circle_mean", "apps.common.aggregate.sum_total"]

    process_ids = measure_process_id
    if aggregated:
        process_ids = aggregated_process_id

    process = Process.objects.filter(name_id__in=process_ids)

    return model.objects.filter(
        phenomenon_time_range__contained_by=pt_range,
        procedure__in=process,
    ).count()
