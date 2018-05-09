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
        'unit': '',
        "default_mean": 'apps.common.aggregate.arithmetic_mean'
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
