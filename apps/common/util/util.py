from apps.utils.obj import *
from apps.common.models import Property, Process, Topic

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

