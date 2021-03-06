# mandatory, dictionary, at least one topic must be specified
TOPICS = {
    # common.Topic.name_id, dictionary, at least one property must be specified
    # topic represents an emergency situation, e.g. drought or floods
    'drought': {

        # dictionary of properties related to the topic
        # mandatory, at least one property must be specified
        'properties': {

            # common.Property.name_id
            'air_temperature': {

                # dictionary of observation providers of given property
                # mandatory, at least one provider must be specified
                'observation_providers': {

                    # path to Django model
                    # the model must be subclass of common.AbstractObservation
                    'apps.processing.ala.models.Observation': {

                        # mandatory, name_id of common.Process
                        'process': 'apps.common.aggregate.arithmetic_mean'
                    },

                    'apps.processing.ozp.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean'
                    },
                    'apps.processing.pmo.models.WeatherObservation': {
                        'process': 'apps.common.aggregate.arithmetic_mean'
                    },
                },
            },
            'precipitation': {
                'observation_providers': {
                    'apps.processing.ala.models.Observation': {
                        'process': 'apps.common.aggregate.sum_total',
                    },
                    'apps.processing.pmo.models.WeatherObservation': {
                        'process': 'apps.common.aggregate.sum_total',
                    }
                }
            },
            'pm10': {
                'observation_providers': {
                    'apps.processing.ozp.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            },
            'stream_flow': {
                'observation_providers': {
                    'apps.processing.pmo.models.WatercourseObservation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                    'apps.processing.huaihe.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            }
        },
        'time_slots': ['30_days_daily', '24_hour_slot', '1_hour_slot']
    },
    'floods': {

        # dictionary of properties related to the topic
        # mandatory, at least one property must be specified
        'properties': {

            # common.Property.name_id
            'air_temperature': {

                # dictionary of observation providers of given property
                # mandatory, at least one provider must be specified
                'observation_providers': {

                    # path to Django model
                    # the model must be subclass of common.AbstractObservation
                    'apps.processing.ala.models.Observation': {

                        # mandatory, name_id of common.Process
                        'process': 'apps.common.aggregate.arithmetic_mean'
                    },
                    'apps.processing.ozp.models.Observation': {
                        'process': 'measure'
                    }
                },
            },

            'ground_air_temperature': {
                'observation_providers': {
                    'apps.processing.ala.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            }
        },
        'time_slots': ['1_hour_slot', '24_hour_slot', '30_days_daily']
    },

    # ...
}

TIME_SLOTS = {
    "1_hour_slot": {
        'zero': '2000-01-01T00:00:00+01:00',
        'frequency': 'PT1H',
        'range_from': 'PT0S',
        'range_to': 'PT1H',
        'name': '1_hour_slot'
    },
    "24_hour_slot": {
        'zero': '2000-01-01T00:00:00+01:00',
        'frequency': 'PT24H',
        'range_from': 'PT0S',
        'range_to': 'PT24H',
        'name': '24_hour_slot'
    },
    "30_days_daily": {
        'zero': '2000-01-01T00:00:00+01:00',
        'frequency': 'P1D',
        'range_from': 'P0D',
        'range_to': 'P30D',
        'name': '30_days_daily',
    },
}

AGGREGATED_OBSERVATIONS = [

    # dictionary representing set of aggregated observations
    {

        # mandatory, definition of common.TimeSeries
        'time_slots': [
            {'id': '1_hour_slot', 'process': 'measure'},
            {'id': '24_hour_slot', 'referenceTimeSlots': '1_hour_slot'},
            {'id': '30_days_daily', 'referenceTimeSlots': '24_hour_slot'},
        ],

        # dictionary of observation providers
        # mandatory, at least one provider must be specified
        'observation_providers': {

            # path to Django model
            # the model must be subclass of common.AbstractObservation
            'apps.processing.ala.models.Observation': {

                # mandatory, name_id of common.Process
                'process': 'measure',

                # mandatory, list of name_ids of common.Property
                'observed_properties': ['precipitation', 'air_temperature'],
            },

            'apps.processing.pmo.models.WatercourseObservation': {
                'process': 'measure',
                'observed_properties': ['stream_flow'],
            },

            'apps.processing.pmo.models.WeatherObservation': {
                'process': 'measure',
                'observed_properties': ['precipitation', 'air_temperature'],
            },

            'apps.processing.ozp.models.Observation': {
                'process': 'measure',
                'observed_properties': ['pm10', 'air_temperature'],
            },

        },

        'properties': {
            'precipitation': [
                'apps.common.aggregate.arithmetic_mean',
                'apps.common.aggregate.sum_total'
            ]
        }
    },

    {
        'time_slots': [
            {'id': '24_hour_slot', 'process': 'measure'},
            {'id': '30_days_daily', 'referenceTimeSlots': '24_hour_slot'},
        ],

        'observation_providers': {
            'apps.processing.huaihe.models.Observation': {
                'process': 'measure',
                'observed_properties': ['stream_flow', 'water_level'],
            },

        },

        'properties': {
        }
    },
]
