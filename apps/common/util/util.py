from apps.utils.obj import *
from apps.common.models import Property, Process
from psycopg2.extras import DateTimeTZRange

props_def = [
    ('precipitation', {
        "name": 'precipitation',
        'unit': 'mm',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('air_temperature', {
        "name": 'air temperature',
        'unit': '°C',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('air_humidity', {
        "name": 'air humidity',
        'unit': '?',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('ground_air_temperature', {
        "name": 'ground air temperature',
        'unit': '°C',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('soil_temperature', {
        "name": 'soil temperature',
        'unit': '°C',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('power_voltage', {
        "name": 'power voltage',
        'unit': 'V',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('wind_speed', {
        "name": 'wind speed',
        "unit": 'm/s',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('wind_direction', {
        "name": 'wind direction',
        "unit": '°',
        "default_mean": 'apps.common.aggregate.circle_mean'
    }),
    ('solar_energy', {
        "name": 'solar energy',
        "unit": 'W/m²',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('atmospheric_pressure', {
        "name": 'atmospheric pressure ',
        'unit': 'hPa',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('co', {
        "name": 'CO',
        'unit': 'mg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('no', {
        "name": 'NO',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('no2', {
        "name": 'NO₂',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('nox', {
        "name": 'NOₓ',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('o3', {
        "name": 'O₃',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('pm1', {
        "name": 'PM1',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('pm2.5', {
        "name": 'PM2.5',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('pm10', {
        "name": 'PM10',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('so2', {
        "name": 'SO₂',
        'unit': 'µg/m³',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
    }),
    ('occuring_events', {
        "name": 'occuring events',
        'unit': ''
    }),
    ('number_of_emerged_events', {
        "name": 'number of emerged events',
        'unit': ''
    }),
]

processes_def = [
    ('measure', {'name': u'measuring'}),
    ('observation', {'name': u'observation'}),
    ('avg_hour', {'name': u'hourly average'}),
    ('avg_day', {'name': u'daily average'}),
    ('apps.common.aggregate.arithmetic_mean', {'name': u'arithmetic mean'}),
    ('apps.common.aggregate.circle_mean', {'name': u'circle mean'}),
]

def get_or_create_props():
    for prop in props_def:
        if 'default_mean' in prop[1]:
            mean = prop[1]['default_mean']
            if not isinstance(prop[1]['default_mean'], Process):
                mean_process = Process.objects.get(name_id=mean)
                if mean and mean_process:
                    prop[1]['default_mean'] = mean_process
                else:
                    prop[1]['default_mean'] = None

    return get_or_create_objs(Property, props_def, 'name_id')


def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')

#TODO consult years, months
intervals = {
    "years": 29030400,  # 60 * 60 * 24 * 7 * 4 * 12
    "months": 2419200,  # 60 * 60 * 24 * 7 * 4
    "weeks": 604800,    # 60 * 60 * 24 * 7
    "days": 86400,      # 60 * 60 * 24
    "hours": 3600,      # 60 * 60
    "minutes": 60,
    "seconds": 1,
}


# TODO validate params - return exceptions
# TODO in case frequency is months or years => zero day <= 28
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

    if (first_interval_counter >= 0) and (last_interval_counter > first_interval_counter):
        for N in range(first_interval_counter, last_interval_counter):
            slot = DateTimeTZRange(
                lower=timeseries.zero + N * timeseries.frequency + timeseries.range_from,
                upper=timeseries.zero + N * timeseries.frequency + timeseries.range_to)
            # Check if slot is after from_datetime
            if from_datetime <= slot.upper:
                condition = True
                if range_from_limit and slot.lower < range_from_limit:
                    condition = False

                if range_to_limit and slot.upper >= range_to_limit:
                    condition = False

                if condition:
                    #print('--------------------------------------------')
                    #print(slot)
                    slots.append(slot)

    return slots
